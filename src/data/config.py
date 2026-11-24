"""전처리 스크립트의 Hydra 설정 도우미."""

import logging
from pathlib import Path
from types import SimpleNamespace

from omegaconf import DictConfig, OmegaConf

# Hydra가 설정을 읽기 전에 필요하므로 코드에 둔다. 이 파일 기준 상대 경로다.
CONFIG_PATH = "../../configs/prep"


def setup_logging(level, levels):
    if level not in levels:
        raise ValueError(f"log_level은 {levels} 중 하나여야 합니다: {level}")
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def to_args(cfg: DictConfig, paths=()):
    """설정을 속성으로 읽는 객체로 바꾼다. paths의 키는 Path로 바꾼다."""
    values = OmegaConf.to_container(cfg, resolve=True)
    for key in paths:
        values[key] = Path(values[key])
    return SimpleNamespace(**values)
