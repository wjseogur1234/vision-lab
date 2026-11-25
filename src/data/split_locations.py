import csv
import logging
import random
from collections import defaultdict

import yaml
from tqdm import tqdm

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
    penalty = 0
    for index, group in enumerate(groups):
        seen_kinds = set().union(*(stats[name]["kinds"] for name in group))
        seen_heights = set().union(*(stats[name]["heights"] for name in group))
        penalty += len(kinds - seen_kinds) + len(heights - seen_heights)
        if index > 0:
            large = sum(stats[name]["person_images"] >= min_person_images for name in group)
            penalty += max(0, min_locations - large)
    counts = [sum(stats[name]["person_images"] for name in group) for group in groups]
    error = sum(abs(counts[i] - targets[i]) for i in range(len(groups))) / sum(targets)
    return penalty, error


def propose(stats, ratios, seed, trials, min_locations, min_person_images, kinds, heights):
    total = sum(item["person_images"] for item in stats.values())
    split_count = len(ratios)
    targets = [ratio * total for ratio in ratios]
    kinds, heights = set(kinds), {str(height) for height in heights}
    train_only = sorted(name for name in stats if stats[name]["kinds"] - kinds)
    names = sorted(name for name in stats if name not in train_only)
    rng = random.Random(seed)

    def evaluate(assign):
        groups = [list(train_only) if i == 0 else [] for i in range(split_count)]
        for name, index in assign.items():
            groups[index].append(name)
        return score(stats, groups, targets, kinds, heights, min_locations, min_person_images), groups

    best = None
    for _ in tqdm(range(trials), desc="분할 탐색", unit="회"):
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


def group_summary(stats, group):
    return {
        "locations": len(group),
        "images": sum(stats[name]["images"] for name in group),
        "person_images": sum(stats[name]["person_images"] for name in group),
        "kinds": sorted(set().union(*(stats[name]["kinds"] for name in group))),
        "heights": sorted(set().union(*(stats[name]["heights"] for name in group))),
    }


def write_split_plan(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        stream.write("# scripts/propose_splits.py가 만든 안이다. 검토 후 고정한다.\n")
        yaml.safe_dump(document, stream, allow_unicode=True, sort_keys=False)
