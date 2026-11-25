import logging
from pathlib import Path
from types import SimpleNamespace

from omegaconf import DictConfig, OmegaConf

CONFIG_PATH = "../configs/prep"


def setup_logging(level, levels):
    if level not in levels:
        raise ValueError(f"log_level은 {levels} 중 하나여야 합니다: {level}")
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def to_args(cfg: DictConfig, paths=()):
    values = OmegaConf.to_container(cfg, resolve=True)
    for key in paths:
        values[key] = Path(values[key])
    return SimpleNamespace(**values)
