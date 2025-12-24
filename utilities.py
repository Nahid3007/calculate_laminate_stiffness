import numpy as np
import logging
import json
import atexit
from pathlib import Path
from typing import Tuple, List

# Laminate properties are based on: 
# https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf

def ply_stiffness(E1: float, 
                  E2: float, 
                  G12: float, 
                  nu12: int) -> np.ndarray:
    """
    Returns reduced stiffness matrix Q for an orthotropic ply
    """
    nu21 = nu12 * E2 / E1
    denom = 1.0 - nu12 * nu21

    Q11 = E1 / denom
    Q22 = E2 / denom
    Q12 = nu12 * E2 / denom
    Q66 = G12

    Q = np.array([
        [Q11, Q12, 0.0],
        [Q12, Q22, 0.0],
        [0.0, 0.0, Q66]
    ])

    return Q


def transform_Q(Q: np.ndarray, 
                theta_deg: int) -> list[np.ndarray]:
    """
    Transforms Q to laminate coordinates at angle theta (degrees)
    """
    theta = np.deg2rad(theta_deg)
    m = np.cos(theta)
    n = np.sin(theta)

    Q11, Q12, Q22, Q66 = Q[0,0], Q[0,1], Q[1,1], Q[2,2]

    Qbar = np.zeros((3,3))

    Qbar[0,0] = Q11*m**4 + Q22*n**4 + 2*(Q12 + 2*Q66)*m**2*n**2
    Qbar[1,1] = Q11*n**4 + Q22*m**4 + 2*(Q12 + 2*Q66)*m**2*n**2
    Qbar[0,1] = (Q11 + Q22 - 4*Q66)*m**2*n**2 + Q12*(m**4 + n**4)
    Qbar[1,0] = Qbar[0,1]

    Qbar[0,2] = (Q11 - Q12 - 2*Q66)*m**3*n - (Q22 - Q12 - 2*Q66)*m*n**3
    Qbar[2,0] = Qbar[0,2]

    Qbar[1,2] = (Q11 - Q12 - 2*Q66)*m*n**3 - (Q22 - Q12 - 2*Q66)*m**3*n
    Qbar[2,1] = Qbar[1,2]

    Qbar[2,2] = (Q11 + Q22 - 2*Q12 - 2*Q66)*m**2*n**2 + Q66*(m**4 + n**4)

    return Qbar


def laminate_ABD(plies: list[dict]) -> list[np.ndarray]:
    """
    Computes A, B, D matrices

    plies: list of dicts with keys:
        Qbar  : transformed stiffness matrix
        z_bot : bottom z-coordinate
        z_top : top z-coordinate
    """
    A = np.zeros((3,3))
    B = np.zeros((3,3))
    D = np.zeros((3,3))

    for ply in plies:
        Qbar = ply['Qbar']
        z0, z1 = ply['z_bot'], ply['z_top']

        A += Qbar * (z1 - z0)
        B += 0.5 * Qbar * (z0**2 - z1**2)
        D += (1.0/3.0) * Qbar * (z1**3 - z0**3)

    return A, B, D


def homogenized_stiffness(A: np.ndarray, 
                          total_thickness: float) -> np.ndarray:
    """
    Returns effective in-plane stiffness matrix
    """
    return A / total_thickness


def effective_free_laminate(A: np.ndarray, 
                            B: np.ndarray,
                            D: np.ndarray, 
                            total_thickness: float) -> np.ndarray: 
    """Effective in-plane stiffness for free unsymmetric laminate"""
    A_star = A - B @ np.linalg.inv(D) @ B
    C_eff = A_star / total_thickness

    return C_eff


def effective_properties(C: np.ndarray) -> list[float]:
    S = np.linalg.inv(C)

    E11 = 1 / S[0,0]
    E22 = 1 / S[1,1]
    G12 = 1 / S[2,2]
    nu12 = -S[0,1] / S[0,0]

    return E11, E22, G12, nu12

def read_input(input_file: Path) -> Tuple[float, float, float, float, float, List[int]]:
    
    json_file = Path(input_file)

    with open(json_file, "r") as f:
        data = json.load(f)

    # Access json input data
    E11 = data["Stiffness properties"]["E1"]
    E22 = data["Stiffness properties"]["E2"]
    G12 = data["Stiffness properties"]["G12"]
    nu12 = data["Stiffness properties"]["nu12"]

    t_ply = data["Ply thickness"]["t_ply"]

    ply_angle_list = data["Stacking sequence"]["angles"]

    return E11, E22, G12, nu12, t_ply, ply_angle_list


def setup_logger(
    name: str = __name__,
    log_file: str = "laminate_analysis.log",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a logger instance with automatic cleanup.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(formatter)

    # Console handler (optional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Automatically close handlers on program exit
    def close_handlers():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    atexit.register(close_handlers)

    return logger