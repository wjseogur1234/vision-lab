import logging

import hydra
from _common import CONFIG_PATH, setup_logging, to_args

from data.split_locations import group_summary, location_stats, propose, write_split_plan

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="propose_splits")
def main(cfg):
    args = to_args(cfg, paths=("manifest", "output"))
    setup_logging(args.log_level, args.log_levels)
    split_names = list(args.ratios)
    ratios = list(args.ratios.values())

    stats = location_stats(args.manifest)
    logger.info("manifest: %s (장소 %d곳)", args.manifest, len(stats))
    groups = propose(
        stats, ratios, args.seed, args.trials, args.min_locations, args.min_person_images,
        args.required_kinds, args.required_heights,
    )
    write_split_plan(args.output, {
        "source_manifest": args.manifest.as_posix(),
        "unit": "location",
        "ratios": args.ratios,
        "seed": args.seed,
        "min_locations": args.min_locations,
        "min_person_images": args.min_person_images,
        "splits": dict(zip(split_names, groups)),
    })
    total = sum(item["person_images"] for item in stats.values())
    for split, group in zip(split_names, groups):
        summary = group_summary(stats, group)
        logger.info(
            "%s: 장소 %d, 이미지 %d, 보행자 이미지 %d (%.1f%%), 카메라 %s, 높이 %s",
            split, summary["locations"], summary["images"], summary["person_images"],
            summary["person_images"] / total * 100, summary["kinds"], summary["heights"],
        )
    logger.info("분할 안 저장: %s", args.output)


if __name__ == "__main__":
    main()
