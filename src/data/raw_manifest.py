"""AI Hub 원본 파일과 라벨의 대응을 CSV로 기록한다."""

import argparse
import csv
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import NamedTuple

from PIL import Image
from tqdm import tqdm

FIELDS = (
    "source_split", "batch", "media_type", "file_name", "label_file", "label_image_id",
    "match_status", "location", "camera", "action", "video_id", "weather", "time_of_day",
    "width", "height", "num_persons",
)
TIME_OF_DAY = {"새벽": "dawn", "오전": "morning", "낮": "day", "오후": "afternoon"}
IMAGE_SUFFIXES = {".jpg", ".jpeg"}


class Label(NamedTuple):
    path: Path
    metadata: dict


def source_files(root):
    data = root / "01.데이터"
    splits = sorted(data.glob("*.*"))
    if not splits:
        raise ValueError(f"원본 분할 폴더가 없습니다: {data}")
    for split in splits:
        if not split.is_dir():
            continue
        for folder, dirs, names in os.walk(split):
            dirs.sort()
            for name in sorted(names):
                yield split.name, Path(folder) / name


def load_json(path):
    with path.open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def bbox_labels(path):
    data = load_json(path)
    meta_by_id = {meta["id"]: meta for meta in data["meta"]}
    counts = Counter()
    for annotation in data["annotations"]:
        counts[annotation["image_id"]] += annotation["category_id"].count(7)
    location, camera = path.parent.parent.name, path.parent.name
    for image in data["images"]:
        image_id = image["id"]
        filename = image["file_name"].replace("\\", "/").rsplit("/", 1)[-1]
        meta = meta_by_id.get(image.get("meta_id"), {})
        yield (location.casefold(), camera.casefold(), filename.casefold()), Label(
            path,
            {
                "label_image_id": image_id,
                "location": location,
                "camera": camera,
                "weather": str(meta.get("weather") or "").strip().lower() or "unknown",
                "time_of_day": TIME_OF_DAY.get(meta.get("time_space"), "unknown"),
                "num_persons": counts[image_id],
            },
        )


def voc_label(path):
    annotation = ET.parse(path).getroot()
    return Label(
        path,
        {
            "action": path.parent.parent.name,
            "video_id": path.parent.name,
            "num_persons": sum(
                obj.findtext("name", "").strip().casefold() == "person"
                for obj in annotation.findall("object")
            ),
        },
    )


def index_dataset(root, dataset):
    media = defaultdict(list)
    labels = defaultdict(list)
    files = tqdm(source_files(root), desc=f"{dataset} 파일 찾기", unit="개")
    for split, path in files:
        parts = path.relative_to(root).parts
        suffix = path.suffix.lower()
        if dataset == "101":
            if parts[2] != "교통안전(Bbox)":
                continue
            if suffix == ".json":
                for key, label in bbox_labels(path):
                    labels[(split, "", *key)].append(label)
            elif suffix in IMAGE_SUFFIXES:
                location, camera = path.parent.parent.name, path.parent.name
                key = (split, "", location.casefold(), camera.casefold(), path.name.casefold())
                media[key].append(path)
            continue

        # 원천과 라벨 폴더에서 같은 추가분 접미사를 사용한다.
        folder = parts[2]
        stem = path.stem.casefold()
        if dataset == "095":
            key = (split, "", stem)
            if folder.startswith("원천데이터") and suffix == ".mp4":
                media[key].append(path)
            elif folder.startswith("라벨링데이터") and suffix == ".json":
                labels[key].append(Label(path, {"video_id": path.stem}))
        else:
            action, video = path.parent.parent.name, path.parent.name
            key = (split, folder.partition("_")[2], action.casefold(), video.casefold(), stem)
            if folder.startswith("원천데이터") and suffix in IMAGE_SUFFIXES:
                media[key].append(path)
            elif folder.startswith("라벨링데이터") and suffix == ".xml":
                labels[key].append(voc_label(path))
    if not media and not labels:
        raise ValueError(f"원본이나 라벨 파일이 없습니다: {root}")
    return media, labels


def manifest_rows(root, dataset):
    media, labels = index_dataset(root, dataset)
    keys = sorted(media.keys() | labels.keys())
    for key in tqdm(keys, desc=f"{dataset} 매칭·크기 읽기", unit="개"):
        files, annotations = media.get(key, []), labels.get(key, [])
        base = {
            "source_split": key[0],
            "batch": key[1],
            "media_type": "video" if dataset == "095" else "image",
        }
        if len(files) > 1 or len(annotations) > 1:
            pairs = [(path, None, "ambiguous") for path in files]
            pairs += [(None, label, "ambiguous") for label in annotations]
        elif files and annotations:
            pairs = [(files[0], annotations[0], "matched")]
        elif files:
            pairs = [(files[0], None, "missing_label")]
        else:
            pairs = [(None, annotations[0], "missing_media")]

        for path, label, status in pairs:
            row = standard_row(root, dataset, path, label)
            yield base | row | {"match_status": status}


def standard_row(root, dataset, path, label):
    row = {}
    if path is not None:
        row["file_name"] = path.relative_to(root).as_posix()
        if dataset == "095":
            row["video_id"] = path.stem
        else:
            with Image.open(path) as image:
                row["width"], row["height"] = image.size
            if dataset == "101":
                row.update(location=path.parent.parent.name, camera=path.parent.name)
            else:
                row.update(action=path.parent.parent.name, video_id=path.parent.name)
    if label is not None:
        row.update(label.metadata)
        row["label_file"] = label.path.relative_to(root).as_posix()
    return row


def write_manifest(root, dataset, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = Counter()
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=destination.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        try:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            for row in manifest_rows(root, dataset):
                writer.writerow(row)
                rows[row["match_status"]] += 1
            stream.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/interim/raw-manifests"))
    parser.add_argument("--dataset", nargs="+", choices=("095", "101", "110"))
    args = parser.parse_args()
    for dataset in dict.fromkeys(args.dataset or ("095", "101", "110")):
        roots = sorted(path for path in args.raw_dir.glob(f"{dataset}.*") if path.is_dir())
        if len(roots) != 1:
            parser.error(f"{args.raw_dir}에서 {dataset}.* 폴더를 하나 찾을 수 있어야 합니다.")
        destination = args.output_dir / dataset / "manifest.csv"
        try:
            rows = write_manifest(roots[0], dataset, destination)
        except (OSError, ValueError, KeyError, ET.ParseError) as error:
            parser.exit(1, f"{dataset}: {error}\n")
        summary = ", ".join(f"{status}={count}" for status, count in sorted(rows.items()))
        print(f"{destination}: {summary}", flush=True)


if __name__ == "__main__":
    main()
