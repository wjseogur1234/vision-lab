import logging
import sys

import hydra
from _common import CONFIG_PATH, setup_logging, to_args
from hydra.core.hydra_config import HydraConfig
from tqdm.contrib.logging import logging_redirect_tqdm

from data.build_coco import collect, free_name, load_splits, select, write_config, write_dataset

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="build_coco")
def main(cfg):
    paths = ("manifest", "raw_dir", "output_dir", "config_dir")
    args = to_args(cfg, paths=paths)
    setup_logging(args.log_level, args.log_levels)
    splits_file = f"configs/data/{HydraConfig.get().runtime.choices['data@split_plan']}.yaml"
    if not 0 <= args.background_ratio < 1 or not 0 < args.fraction <= 1:
        logger.error("background_ratio는 [0, 1), fraction은 (0, 1] 범위여야 합니다.")
        sys.exit(2)

    if not args.overwrite:
        name = free_name(args.name, args.output_dir, args.config_dir)
        if name != args.name:
            logger.warning("%s이 이미 있어 %s로 만듭니다.", args.name, name)
        args.name = name
    destination = args.output_dir / args.name
    try:
        split_names, split_of = load_splits(args.split_plan)
        logger.info("분할 안: %s (분할 %s, 장소 %d곳)", splits_file, split_names, len(split_of))
        with logging_redirect_tqdm():
            items, issues = collect(
                args.manifest, args.raw_dir / args.dataset_folder, args.dataset_folder,
                split_names, split_of, args.source_category,
            )
            selected = select(
                items, split_names, args.background_ratio, args.fraction, args.seed
            )
            metadata = write_dataset(
                destination, selected, issues, split_names, args.class_name,
                args.manifest_fields, args.issue_fields,
                provenance={
                    "command": " ".join(sys.argv),
                    "source_manifest": args.manifest.as_posix(),
                    "splits_file": splits_file,
                    "dataset_folder": args.dataset_folder,
                    "image_root": "data/raw",
                    "classes": {1: args.class_name},
                    "source_category": args.source_category,
                    "background_ratio": args.background_ratio,
                    "fraction": args.fraction,
                    "seed": args.seed,
                },
                overwrite=args.overwrite,
            )
    except (OSError, ValueError, KeyError) as error:
        logger.error("%s", error)
        sys.exit(1)
    write_config(
        args.config_dir / f"{args.name}.yaml", destination, args.raw_dir,
        split_names, args.class_name,
    )
    for split, counts in metadata["summary"].items():
        logger.info("%s 결과: %s", split, counts)


if __name__ == "__main__":
    main()
