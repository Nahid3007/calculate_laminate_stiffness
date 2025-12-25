from pathlib import Path
import logging
from dataclasses import dataclass
from typing import List
import json


@dataclass(frozen=True)
class LaminateInput:
    E1: float
    E2: float
    G12: float
    nu12: float
    t_ply: float
    ply_angles: List[int]


def read_input(input_file: Path) -> LaminateInput:
    input_file = Path(input_file)

    with input_file.open("r") as f:
        data = json.load(f)

    return LaminateInput(
        E1=data["Stiffness properties"]["E1"],
        E2=data["Stiffness properties"]["E2"],
        G12=data["Stiffness properties"]["G12"],
        nu12=data["Stiffness properties"]["nu12"],
        t_ply=data["Ply thickness"]["t_ply"],
        ply_angles=data["Stacking sequence"]["angles"],
    )


def setup_logger(
    name: str,
    log_file: Path,
    level: int = logging.INFO
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
