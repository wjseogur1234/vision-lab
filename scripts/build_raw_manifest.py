import sys
import xml.etree.ElementTree as ET

import hydra
from _common import CONFIG_PATH, to_args

from data.raw_manifest import find_dataset_root, write_manifest


@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="build_raw_manifest")
def main(cfg):
    args = to_args(cfg, paths=("raw_dir", "output_dir"))
    datasets = [str(name).zfill(3) for name in args.dataset]
    unknown = set(datasets) - set(args.known_datasets)
    if unknown:
        sys.exit(f"알 수 없는 dataset: {sorted(unknown)}")
    for dataset in dict.fromkeys(datasets):
        destination = args.output_dir / dataset / "manifest.csv"
        try:
            root = find_dataset_root(args.raw_dir, dataset)
            rows = write_manifest(
                root, dataset, destination, args.fields, args.image_suffixes, args.time_of_day
            )
        except (OSError, ValueError, KeyError, ET.ParseError) as error:
            sys.exit(f"{dataset}: {error}")
        summary = ", ".join(f"{status}={count}" for status, count in sorted(rows.items()))
        print(f"{destination}: {summary}", flush=True)


if __name__ == "__main__":
    main()
