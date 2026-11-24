"""101 Bbox의 장소를 train, val, test에 배정하는 안을 만든다.

보행자가 있는 이미지 수로 목표 비율에 맞춘다.
결과는 YAML로 쓴다. 사람이 검토한 뒤 git에 올린다.
"""

import csv
import logging
import random
from collections import defaultdict

import hydra
import yaml
from tqdm import tqdm

from data.config import CONFIG_PATH, setup_logging, to_args

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


def propose(stats, ratios, seed, trials, min_locations, min_person_images, kinds, heights):
    total = sum(item["person_images"] for item in stats.values())
    split_count = len(ratios)
    targets = [ratio * total for ratio in ratios]
    # kinds 밖의 카메라 종류(AY)가 있는 장소는 train에 고정한다.
    kinds, heights = set(kinds), {str(height) for height in heights}
    fixed = sorted(name for name in stats if stats[name]["kinds"] - kinds)
    names = sorted(name for name in stats if name not in fixed)
    rng = random.Random(seed)

    def evaluate(assign):
        groups = [list(fixed) if i == 0 else [] for i in range(split_count)]
        for name, index in assign.items():
            groups[index].append(name)
        return score(stats, groups, targets, kinds, heights, min_locations, min_person_images), groups

    best = None
    for _ in tqdm(range(trials), desc="분할 탐색", unit="회"):
        # 무작위로 시작한 뒤 장소 이동과 맞교환으로 점수를 낮춘다.
        assign = {name: rng.choices(range(split_count), weights=ratios)[0] for name in names}
        current, _ = evaluate(assign)
        improved = True
        while improved:
            improved = False
            for name in names:
                for index in range(split_count):
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


@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="split_locations")
def main(cfg):
    args = to_args(cfg, paths=("manifest", "output"))
    setup_logging(args.log_level, args.log_levels)
    # ratios의 키 순서가 분할 순서다. 첫 분할이 train이다.
    split_names = list(args.ratios)
    ratios = list(args.ratios.values())

    stats = location_stats(args.manifest)
    logger.info("manifest: %s (장소 %d곳)", args.manifest, len(stats))
    groups = propose(
        stats, ratios, args.seed, args.trials, args.min_locations, args.min_person_images,
        args.required_kinds, args.required_heights,
    )
    total = sum(item["person_images"] for item in stats.values())
    document = {
        "source_manifest": args.manifest.as_posix(),
        "unit": "location",
        "ratios": args.ratios,
        "seed": args.seed,
        "min_locations": args.min_locations,
        "min_person_images": args.min_person_images,
        "splits": dict(zip(split_names, groups)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        stream.write("# split_locations.py가 만든 안이다. 검토 후 고정한다.\n")
        yaml.safe_dump(document, stream, allow_unicode=True, sort_keys=False)
    for split, group in zip(split_names, groups):
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
