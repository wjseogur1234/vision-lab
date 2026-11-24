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


def score(stats, groups, targets, kinds, heights, min_locations, min_person_images):
    """(조건 위반 수, 비율 오차)를 돌려준다. 작을수록 좋다."""
    penalty = 0
    for index, group in enumerate(groups):
        seen_kinds = set().union(*(stats[name]["kinds"] for name in group))
        seen_heights = set().union(*(stats[name]["heights"] for name in group))
        penalty += len(kinds - seen_kinds) + len(heights - seen_heights)
        if index > 0:
            # val, test에 보행자 이미지가 충분한 장소를 min_locations곳 이상 둔다.
            large = sum(stats[name]["person_images"] >= min_person_images for name in group)
            penalty += max(0, min_locations - large)
    counts = [sum(stats[name]["person_images"] for name in group) for group in groups]
    error = sum(abs(counts[i] - targets[i]) for i in range(len(groups))) / sum(targets)
    return penalty, error


def propose(stats, ratios, seed, trials, min_locations, min_person_images):
    total = sum(item["person_images"] for item in stats.values())
    targets = [ratio * total for ratio in ratios]
    # 모든 분할에 둘 카메라 종류와 높이. 장소 1~2곳뿐인 종류(AY)는 빼고 train에 둔다.
    kinds, heights = {"BC", "SC"}, {"1080", "720"}
    fixed = sorted(name for name in stats if stats[name]["kinds"] - kinds)
    names = sorted(name for name in stats if name not in fixed)
    rng = random.Random(seed)

    def evaluate(assign):
        groups = [list(fixed) if i == 0 else [] for i in range(len(SPLITS))]
        for name, index in assign.items():
            groups[index].append(name)
        return score(stats, groups, targets, kinds, heights, min_locations, min_person_images), groups

    best = None
    for _ in tqdm(range(trials), desc="분할 탐색", unit="회"):
        # 무작위로 시작한 뒤 장소 이동과 맞교환으로 점수를 낮춘다.
        assign = {name: rng.choices(range(len(SPLITS)), weights=ratios)[0] for name in names}
        current, _ = evaluate(assign)
        improved = True
        while improved:
            improved = False
            for name in names:
                for index in range(len(SPLITS)):
                    if assign[name] == index:
                        continue
                    old, assign[name] = assign[name], index
                    candidate, _ = evaluate(assign)
                    if candidate < current:
                        current, improved = candidate, True
                    else:
                        assign[name] = old
            for i, first in enumerate(names):
                for second in names[i + 1:]:
                    if assign[first] == assign[second]:
                        continue
                    assign[first], assign[second] = assign[second], assign[first]
                    candidate, _ = evaluate(assign)
                    if candidate < current:
                        current, improved = candidate, True
                    else:
                        assign[first], assign[second] = assign[second], assign[first]
        if current[0] == 0 and (best is None or current[1] < best[0]):
            best = (current[1], [sorted(group) for group in evaluate(assign)[1]])
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
        "--output", type=Path, default=Path("configs/data/aihub101-ped-v2.splits.yaml")
    )
    parser.add_argument("--ratios", type=float, nargs=3, default=(0.7, 0.15, 0.15))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument(
        "--min-locations", type=int, default=6,
        help="val, test에 둘 큰 장소의 최소 수",
    )
    parser.add_argument(
        "--min-person-images", type=int, default=500,
        help="큰 장소로 셀 보행자 이미지 수의 하한",
    )
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING"))
    args = parser.parse_args()
    setup_logging(args.log_level)

    stats = location_stats(args.manifest)
    logger.info("manifest: %s (장소 %d곳)", args.manifest, len(stats))
    groups = propose(
        stats, args.ratios, args.seed, args.trials, args.min_locations, args.min_person_images
    )
    total = sum(item["person_images"] for item in stats.values())
    document = {
        "source_manifest": args.manifest.as_posix(),
        "unit": "location",
        "ratios": dict(zip(SPLITS, args.ratios)),
        "seed": args.seed,
        "min_locations": args.min_locations,
        "min_person_images": args.min_person_images,
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
