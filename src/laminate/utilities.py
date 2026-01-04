from pathlib import Path
import logging
import os
import sys
from dataclasses import dataclass
from typing import List
import yaml


@dataclass(frozen=True)
class LaminateInput:
    """
    Represents the input data required for laminate stiffness analysis.

    Parameters
    ----------
    E1 : float
        Longitudinal Young's modulus of the ply (Pa or consistent units).
    E2 : float
        Transverse Young's modulus of the ply (Pa or consistent units).
    G12 : float
        In-plane shear modulus of the ply (Pa or consistent units).
    nu12 : float
        Major Poisson's ratio of the ply.
    t_ply : float
        Thickness of a single ply (m or consistent units).
    ply_angles : List[int]
        List of ply orientation angles in degrees.

    Attribute
    ----------
    no_of_plies : int
        Total number of plies in the laminate.
    t_total : float
        Total laminate thickness (sum of all ply thicknesses).
    """
    E1: float
    E2: float
    G12: float
    nu12: float
    t_ply: float
    ply_angles: List[int]

    @property
    def no_of_plies(self) -> int:
        """
        Number of plies in the laminate.

        Returns
        -------
        int
        """
        return len(self.ply_angles)

    @property
    def t_total(self) -> float:
        """
        Total thickness of the laminate.

        Returns
        -------
        float
        """
        return self.no_of_plies * self.t_ply
    

def read_input(input_file: Path, 
               logger = None) -> LaminateInput:
    """
    Reads laminate input data from a YAML file and returns a LaminateInput object.

    Parameters
    ----------
    input_file : Path
        Path to the YAML input file containing laminate properties.
    logger : logging.Logger, optional
        Logger for informational messages. If None, a default logger is created.

    Returns
    -------
    LaminateInput
        Dataclass containing E1, E2, G12, nu12, ply thickness, and ply angles.

    Raises
    ------
    KeyError
        If expected keys ("Stiffness properties", "Ply thickness", "Stacking sequence")
        are missing from the input file.

    Notes
    -----
    The YAML file should have the following structure:
    
    Stiffness properties:
        E1: <value>
        E2: <value>
        G12: <value>
        nu12: <value>
    Ply thickness:
        t_ply: <value>
    Stacking sequence:
        angles: [angle1, angle2, ...]
    """
    if logger is None:
        logger = logging.getLogger("laminate_stiffness_analysis")

    input_file = Path(input_file)

    with open(input_file, "r") as f:
        data = yaml.safe_load(f)

    try:
        stiffness = data["Stiffness properties"]
        thickness = data["Ply thickness"]
        stacking = data["Stacking sequence"]
    except KeyError as exc:
        print("Invalid input structure: missing %s", exc)
        raise

    laminate_input = LaminateInput(
        E1=stiffness["E1"],
        E2=stiffness["E2"],
        G12=stiffness["G12"],
        nu12=stiffness["nu12"],
        t_ply=thickness["t_ply"],
        ply_angles=stacking["angles"],
    )

    logger.info("Input data loaded from JSON:\n"
        "E1 = %.1f, E2 = %.1f, G12 = %.1f, nu12 = %.3f\n"
        "Ply thickness = %.3f\n"
        "No. of plies = %s\n"
        "Total laminate thickness = %.5f\n"
        "Stacking angles = %s",
        laminate_input.E1, laminate_input.E2, laminate_input.G12, laminate_input.nu12,
        laminate_input.t_ply,
        laminate_input.no_of_plies,
        laminate_input.t_total,
        laminate_input.ply_angles,
    )

    return laminate_input


def setup_logger(
    logPath,
    level=logging.INFO,
    name=None,
    write_to_console=True) -> logging.Logger:
    """
    Configures a logger to write messages to a file and optionally to the console.

    Parameters
    ----------
    logPath : str or Path
        Path to the log file.
    level : int, optional
        Logging level (default is logging.INFO).
    name : str, optional
        Name of the logger. Default is "laminate_stiffness_analysis".
    write_to_console : bool, optional
        If True, also outputs logs to the console. Default is True.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """
    name = name or "laminate_stiffness_analysis"
    logPath = Path(logPath)

    # Ensure log directory exists
    if logPath.parent != Path("."):
        os.makedirs(logPath.parent, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-4.4s %(module)s]: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # File handler
    file_handler = logging.FileHandler(
        logPath, mode="w", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    if write_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def close_logger(logger):
    """
    Closes all handlers of a logger and releases resources.

    Parameters
    ----------
    logger : logging.Logger
        Logger to close.
    """
    logger.info("Closing logger.")
    for h in list(logger.handlers[:]):
        logger.debug(h)
        h.close()
    del logger
