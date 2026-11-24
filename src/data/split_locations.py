"""101 Bbox의 장소를 train, val, test에 배정하는 안을 만든다.

보행자가 있는 이미지 수로 목표 비율에 맞춘다.
결과는 YAML로 쓴다. 사람이 검토한 뒤 git에 올린다.
"""

import argparse
import csv
import logging
import random
from collections import defaultdict
from pathlib import Path

import yaml
from tqdm import tqdm

SPLITS = ("train", "val", "test")

logger = logging.getLogger(__name__)


def location_stats(manifest):
    stats = defaultdict(lambda: {"images": 0, "person_images": 0, "kinds": set(), "heights": set()})
    with manifest.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["match_status"] != "matched":
                continue
            item = stats[row["location"]]
            item["images"] += 1
            item["person_images"] += int(row["num_persons"] or 0) > 0
            item["kinds"].add(row["camera"][:2])
            item["heights"].add(row["height"])
    return dict(stats)


def covers(stats, locations, kinds, heights):
    seen_kinds = set().union(*(stats[name]["kinds"] for name in locations))
    seen_heights = set().union(*(stats[name]["heights"] for name in locations))
    return kinds <= seen_kinds and heights <= seen_heights


def propose(stats, ratios, seed, trials):
    total = sum(item["person_images"] for item in stats.values())
    targets = [ratio * total for ratio in ratios]
    # 모든 분할에 둘 카메라 종류와 높이. 장소 1~2곳뿐인 종류(AY)는 빼고 train에 둔다.
    kinds, heights = {"BC", "SC"}, {"1080", "720"}
    names = sorted(stats)
    rng = random.Random(seed)
    best = None
    for _ in tqdm(range(trials), desc="분할 탐색", unit="회"):
        rng.shuffle(names)
        groups = [[] for _ in SPLITS]
        counts = [0] * len(SPLITS)
        # 큰 장소부터 목표에 가장 모자란 분할에 넣는다.
        for name in sorted(names, key=lambda n: -stats[n]["person_images"]):
            if stats[name]["kinds"] - kinds:
                index = 0
            else:
                gaps = [(targets[i] - counts[i]) / targets[i] + rng.random() * 0.3 for i in range(3)]
                index = max(range(3), key=gaps.__getitem__)
            groups[index].append(name)
            counts[index] += stats[name]["person_images"]
        if not all(covers(stats, group, kinds, heights) for group in groups):
            continue
        error = sum(abs(counts[i] - targets[i]) for i in range(3)) / total
        if best is None or error < best[0]:
            best = (error, [sorted(group) for group in groups])
    logger.info("시도 %d회, 최소 오차 %s", trials, f"{best[0]:.4f}" if best else "없음")
    if best is None:
        raise ValueError("조건을 만족하는 배정을 찾지 못했습니다.")
    return best[1]


def setup_logging(level):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/interim/raw-manifests/101/manifest.csv")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("configs/data/aihub101-ped-v1.splits.yaml")
    )
    parser.add_argument("--ratios", type=float, nargs=3, default=(0.7, 0.15, 0.15))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trials", type=int, default=20000)
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING"))
    args = parser.parse_args()
    setup_logging(args.log_level)

    stats = location_stats(args.manifest)
    logger.info("manifest: %s (장소 %d곳)", args.manifest, len(stats))
    groups = propose(stats, args.ratios, args.seed, args.trials)
    total = sum(item["person_images"] for item in stats.values())
    document = {
        "source_manifest": args.manifest.as_posix(),
        "unit": "location",
        "ratios": dict(zip(SPLITS, args.ratios)),
        "seed": args.seed,
        "splits": dict(zip(SPLITS, groups)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        stream.write("# split_locations.py가 만든 안이다. 검토 후 고정한다.\n")
        yaml.safe_dump(document, stream, allow_unicode=True, sort_keys=False)
    for split, group in zip(SPLITS, groups):
        persons = sum(stats[name]["person_images"] for name in group)
        images = sum(stats[name]["images"] for name in group)
        kinds = sorted(set().union(*(stats[name]["kinds"] for name in group)))
        heights = sorted(set().union(*(stats[name]["heights"] for name in group)))
        logger.info(
            "%s: 장소 %d, 이미지 %d, 보행자 이미지 %d (%.1f%%), 카메라 %s, 높이 %s",
            split, len(group), images, persons, persons / total * 100, kinds, heights,
        )
    logger.info("분할 안 저장: %s", args.output)


if __name__ == "__main__":
    main()
