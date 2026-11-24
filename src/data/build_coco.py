"""101 Bbox 원본 manifest로 LibreYOLO용 COCO 데이터셋을 만든다.

이미지는 복사하지 않는다. COCO `file_name`에 `data/raw/` 기준 원본 경로를 적는다.
"""

import csv
import json
import logging
import random
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import hydra
import yaml
from hydra.core.hydra_config import HydraConfig
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from data.config import CONFIG_PATH, setup_logging, to_args

logger = logging.getLogger(__name__)


def read_manifest(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def load_splits(split_plan):
    """분할 안을 (분할 이름 목록, 장소별 분할)로 바꾼다. 분할 안은 Hydra가 읽는다."""
    split_names = list(split_plan["splits"])
    split_of = {}
    for split in split_names:
        for location in split_plan["splits"][split] or []:
            if location in split_of:
                raise ValueError(f"장소가 두 분할에 있습니다: {location}")
            split_of[location] = split
    return split_names, split_of


def person_boxes(dataset_root, label_file, category_id, cache):
    """라벨 JSON 하나를 읽어 이미지 ID별 보행자 상자 목록을 돌려준다."""
    if label_file not in cache:
        cache.clear()  # 같은 라벨 파일의 행이 이어지므로 하나만 둔다.
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


def collect(args):
    dataset_root = args.raw_dir / args.dataset_folder
    split_names, split_of = load_splits(args.split_plan)
    args.split_names = split_names
    logger.info("분할 안: %s (분할 %s, 장소 %d곳)", args.splits_file, split_names, len(split_of))
    issues = []
    rows = sorted(read_manifest(args.manifest), key=lambda row: row.get("label_file") or "")
    logger.info("manifest: %s (%d행)", args.manifest, len(rows))
    cache = {}
    items = {split: {"person": [], "background": []} for split in args.split_names}
    for row in tqdm(rows, desc="라벨 매칭", unit="장"):
        file_name = f"{args.dataset_folder}/{row['file_name']}" if row["file_name"] else ""
        if row["match_status"] != "matched":
            issues.append((file_name or row["label_file"], row["match_status"], ""))
            continue
        split = split_of.get(row["location"])
        if split is None:
            issues.append((file_name, "unassigned_location", row["location"]))
            continue
        width, height = int(row["width"]), int(row["height"])
        boxes = []
        boxes_by_image = person_boxes(
            dataset_root, row["label_file"], args.source_category, cache
        )
        raw = boxes_by_image.get(int(row["label_image_id"]))
        for box in raw or []:
            clipped = clip_box(box, width, height)
            if clipped[2] <= 0 or clipped[3] <= 0:
                issues.append((file_name, "empty_box", json.dumps(box)))
                continue
            boxes.append(clipped)
        item = {"row": row, "file_name": file_name, "split": split, "boxes": boxes}
        items[split]["person" if boxes else "background"].append(item)
    for split in args.split_names:
        logger.info(
            "%s 후보: 보행자 이미지 %d, 배경 이미지 %d",
            split, len(items[split]["person"]), len(items[split]["background"]),
        )
    for issue, count in sorted(Counter(issue[1] for issue in issues).items()):
        logger.warning("문제 항목 %s: %d건", issue, count)
    return items, issues


def select(items, split_names, background_ratio, fraction, seed):
    """분할마다 배경 이미지를 뽑고, 필요하면 전체를 줄인다."""
    rng = random.Random(seed)
    selected = {}
    for split in split_names:
        persons = sorted(items[split]["person"], key=lambda item: item["file_name"])
        backgrounds = sorted(items[split]["background"], key=lambda item: item["file_name"])
        if fraction < 1:
            persons = rng.sample(persons, round(len(persons) * fraction))
        # 배경이 전체의 background_ratio가 되도록 뽑는다.
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


def write_dataset(args, selected, issues):
    destination = args.output_dir / args.name
    if destination.exists() and not args.overwrite:
        raise FileExistsError(f"이미 있습니다: {destination}. 버전을 올리거나 overwrite=true를 쓴다.")
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.rmtree(temporary, ignore_errors=True)
    (temporary / "annotations").mkdir(parents=True)

    summary = {}
    manifest_rows = []
    for split in tqdm(args.split_names, desc="COCO 쓰기", unit="분할"):
        document = coco_document(selected[split], args.class_name)
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
    write_csv(temporary / "manifest.csv", args.manifest_fields, manifest_rows)
    issue_rows = [dict(zip(args.issue_fields, issue)) for issue in issues]
    write_csv(temporary / "issues.csv", args.issue_fields, issue_rows)

    metadata = {
        "name": args.name,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": " ".join(sys.argv),
        "source_manifest": args.manifest.as_posix(),
        "splits_file": args.splits_file,
        "dataset_folder": args.dataset_folder,
        "image_root": "data/raw",
        "classes": {1: args.class_name},
        "source_category": args.source_category,
        "background_ratio": args.background_ratio,
        "fraction": args.fraction,
        "seed": args.seed,
        "summary": summary,
        "issues": dict(Counter(issue[1] for issue in issues)),
    }
    with (temporary / "metadata.yaml").open("w", encoding="utf-8") as stream:
        yaml.safe_dump(metadata, stream, allow_unicode=True, sort_keys=False)

    if destination.exists():
        shutil.rmtree(destination)
    temporary.rename(destination)
    logger.info("데이터셋 저장: %s", destination)
    return destination, metadata


def write_config(args, destination):
    """LibreYOLO에 넘기는 데이터셋 YAML을 쓴다."""
    image_root = args.raw_dir.absolute().as_posix()
    config = {"path": destination.absolute().as_posix()}
    config |= {split: image_root for split in args.split_names}
    config["annotations"] = {split: f"annotations/{split}.json" for split in args.split_names}
    config["names"] = {0: args.class_name}
    path = args.config_dir / f"{args.name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        stream.write("# build_coco.py가 만든다. 손으로 고치지 않는다.\n")
        yaml.safe_dump(config, stream, allow_unicode=True, sort_keys=False)
    logger.info("LibreYOLO YAML 저장: %s", path)
    return path


@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="build_coco")
def main(cfg):
    paths = ("manifest", "raw_dir", "output_dir", "config_dir")
    args = to_args(cfg, paths=paths)
    setup_logging(args.log_level, args.log_levels)
    # 어떤 분할 파일을 골랐는지 metadata에 남긴다.
    args.splits_file = f"configs/data/{HydraConfig.get().runtime.choices['data@split_plan']}.yaml"
    if not 0 <= args.background_ratio < 1 or not 0 < args.fraction <= 1:
        logger.error("background_ratio는 [0, 1), fraction은 (0, 1] 범위여야 합니다.")
        sys.exit(2)

    try:
        with logging_redirect_tqdm():
            items, issues = collect(args)
            selected = select(
                items, args.split_names, args.background_ratio, args.fraction, args.seed
            )
            destination, metadata = write_dataset(args, selected, issues)
    except (OSError, ValueError, KeyError) as error:
        logger.error("%s", error)
        sys.exit(1)
    write_config(args, destination)
    for split, counts in metadata["summary"].items():
        logger.info("%s 결과: %s", split, counts)


if __name__ == "__main__":
    main()
