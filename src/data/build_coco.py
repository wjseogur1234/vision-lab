import csv
import json
import logging
import random
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone

import yaml
from tqdm import tqdm

logger = logging.getLogger(__name__)

VERSION_SUFFIX = re.compile(r"^(?P<base>.+)-v(?P<number>\d+)$")


def free_name(name, output_dir, config_dir):
    def taken(candidate):
        return (output_dir / candidate).exists() or (config_dir / f"{candidate}.yaml").exists()

    match = VERSION_SUFFIX.match(name)
    base, number = (match["base"], int(match["number"])) if match else (name, 1)
    candidate = name
    while taken(candidate):
        number += 1
        candidate = f"{base}-v{number}"
    return candidate


def read_manifest(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def load_splits(split_plan):
    split_names = list(split_plan["splits"])
    split_of = {}
    for split in split_names:
        for location in split_plan["splits"][split] or []:
            if location in split_of:
                raise ValueError(f"장소가 두 분할에 있습니다: {location}")
            split_of[location] = split
    return split_names, split_of


def person_boxes(dataset_root, label_file, category_id, cache):
    if label_file not in cache:
        cache.clear()
        logger.debug("라벨 읽기: %s", label_file)
        with (dataset_root / label_file).open(encoding="utf-8-sig") as stream:
            data = json.load(stream)
        boxes = defaultdict(list)
        for annotation in data["annotations"]:
            for bbox, category in zip(annotation["bbox"], annotation["category_id"]):
                if category == category_id:
                    boxes[annotation["image_id"]].append(bbox)
        cache[label_file] = boxes
    return cache[label_file]


def clip_box(box, width, height):
    x1, y1, x2, y2 = (float(value) for value in box)
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    x1, x2 = max(0.0, x1), min(float(width), x2)
    y1, y2 = max(0.0, y1), min(float(height), y2)
    return [x1, y1, x2 - x1, y2 - y1]


def collect(manifest, dataset_root, dataset_folder, split_names, split_of, source_category):
    issues = []
    rows = sorted(read_manifest(manifest), key=lambda row: row.get("label_file") or "")
    logger.info("manifest: %s (%d행)", manifest, len(rows))
    cache = {}
    items = {split: {"person": [], "background": []} for split in split_names}
    for row in tqdm(rows, desc="라벨 매칭", unit="장"):
        file_name = f"{dataset_folder}/{row['file_name']}" if row["file_name"] else ""
        if row["match_status"] != "matched":
            issues.append((file_name or row["label_file"], row["match_status"], ""))
            continue
        split = split_of.get(row["location"])
        if split is None:
            issues.append((file_name, "unassigned_location", row["location"]))
            continue
        width, height = int(row["width"]), int(row["height"])
        boxes = []
        boxes_by_image = person_boxes(dataset_root, row["label_file"], source_category, cache)
        raw = boxes_by_image.get(int(row["label_image_id"]))
        for box in raw or []:
            clipped = clip_box(box, width, height)
            if clipped[2] <= 0 or clipped[3] <= 0:
                issues.append((file_name, "empty_box", json.dumps(box)))
                continue
            boxes.append(clipped)
        item = {"row": row, "file_name": file_name, "split": split, "boxes": boxes}
        items[split]["person" if boxes else "background"].append(item)
    for split in split_names:
        logger.info(
            "%s 후보: 보행자 이미지 %d, 배경 이미지 %d",
            split, len(items[split]["person"]), len(items[split]["background"]),
        )
    for issue, count in sorted(Counter(issue[1] for issue in issues).items()):
        logger.warning("문제 항목 %s: %d건", issue, count)
    return items, issues


def select(items, split_names, background_ratio, fraction, seed):
    rng = random.Random(seed)
    selected = {}
    for split in split_names:
        persons = sorted(items[split]["person"], key=lambda item: item["file_name"])
        backgrounds = sorted(items[split]["background"], key=lambda item: item["file_name"])
        if fraction < 1:
            persons = rng.sample(persons, round(len(persons) * fraction))
        wanted = round(len(persons) * background_ratio / (1 - background_ratio))
        backgrounds = rng.sample(backgrounds, min(wanted, len(backgrounds)))
        if len(backgrounds) < wanted:
            logger.warning("%s 배경 이미지 부족: %d/%d", split, len(backgrounds), wanted)
        selected[split] = sorted(persons + backgrounds, key=lambda item: item["file_name"])
        logger.info("%s 선택: 보행자 %d, 배경 %d", split, len(persons), len(backgrounds))
    return selected


def coco_document(items, class_name):
    images, annotations = [], []
    for image_id, item in enumerate(items, start=1):
        row = item["row"]
        images.append({
            "id": image_id,
            "file_name": item["file_name"],
            "width": int(row["width"]),
            "height": int(row["height"]),
        })
        for box in item["boxes"]:
            annotations.append({
                "id": len(annotations) + 1,
                "image_id": image_id,
                "category_id": 1,
                "bbox": [round(value, 2) for value in box],
                "area": round(box[2] * box[3], 2),
                "iscrowd": 0,
            })
    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": class_name}],
    }


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_dataset(
    destination, selected, issues, split_names, class_name,
    manifest_fields, issue_fields, provenance, overwrite=False,
):
    if destination.exists() and not overwrite:
        raise FileExistsError(f"이미 있습니다: {destination}. 버전을 올리거나 overwrite=true를 쓴다.")
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.rmtree(temporary, ignore_errors=True)
    (temporary / "annotations").mkdir(parents=True)

    summary = {}
    manifest_rows = []
    for split in tqdm(split_names, desc="COCO 쓰기", unit="분할"):
        document = coco_document(selected[split], class_name)
        with (temporary / "annotations" / f"{split}.json").open("w", encoding="utf-8") as stream:
            json.dump(document, stream, ensure_ascii=False)
        summary[split] = {
            "images": len(document["images"]),
            "background_images": sum(not item["boxes"] for item in selected[split]),
            "boxes": len(document["annotations"]),
        }
        for item in selected[split]:
            manifest_rows.append(
                item["row"] | {
                    "file_name": item["file_name"],
                    "split": split,
                    "num_persons": len(item["boxes"]),
                }
            )
    write_csv(temporary / "manifest.csv", manifest_fields, manifest_rows)
    issue_rows = [dict(zip(issue_fields, issue)) for issue in issues]
    write_csv(temporary / "issues.csv", issue_fields, issue_rows)

    metadata = {
        "name": destination.name,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **provenance,
        "summary": summary,
        "issues": dict(Counter(issue[1] for issue in issues)),
    }
    with (temporary / "metadata.yaml").open("w", encoding="utf-8") as stream:
        yaml.safe_dump(metadata, stream, allow_unicode=True, sort_keys=False)

    if destination.exists():
        shutil.rmtree(destination)
    temporary.rename(destination)
    logger.info("데이터셋 저장: %s", destination)
    return metadata


def write_config(path, dataset_dir, image_root, split_names, class_name):
    image_root = image_root.absolute().as_posix()
    config = {"path": dataset_dir.absolute().as_posix()}
    config |= {split: image_root for split in split_names}
    config["annotations"] = {split: f"annotations/{split}.json" for split in split_names}
    config["names"] = {0: class_name}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        stream.write("# scripts/build_coco.py가 만든다. 손으로 고치지 않는다.\n")
        yaml.safe_dump(config, stream, allow_unicode=True, sort_keys=False)
    logger.info("LibreYOLO YAML 저장: %s", path)
