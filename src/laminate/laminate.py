from dataclasses import dataclass, field
import numpy as np
from laminate.ply import Ply

# Laminate properties are based on
# REF: https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf


@dataclass
class Laminate:
    plies: list[Ply]
    A: np.ndarray = field(init=False)
    B: np.ndarray = field(init=False)
    D: np.ndarray = field(init=False)

    def __post_init__(self):
        self._assign_z_coordinates()
        self._compute_ABD()

    @property
    def total_thickness(self) -> float:
        return sum(ply.thickness for ply in self.plies)

    def _assign_z_coordinates(self):
        z = -self.total_thickness / 2.0
        for ply in self.plies:
            ply.z_bot = z
            z += ply.thickness
            ply.z_top = z

    def _compute_ABD(self):
        self.A = np.zeros((3, 3))
        self.B = np.zeros((3, 3))
        self.D = np.zeros((3, 3))

        for ply in self.plies:
            Qbar = ply.lamina_stiffness_matrix
            z0, z1 = ply.z_bot, ply.z_top

            self.A += Qbar * (z1 - z0)
            self.B += 0.5 * Qbar * (z0**2 - z1**2)
            self.D += (1.0 / 3.0) * Qbar * (z1**3 - z0**3)

    @property
    def is_symmetric(self) -> bool:
        return np.allclose(self.B, 0.0, atol=1e-8)

    @property
    def C_eff(self) -> np.ndarray:
        if self.is_symmetric:
            return self.A / self.total_thickness
        else:
            A_star = self.A - self.B @ np.linalg.inv(self.D) @ self.B
            return A_star / self.total_thickness

    @property
    def effective_properties(self) -> dict:
        S = np.linalg.inv(self.C_eff)
        return {
            "E1": 1.0 / S[0, 0],
            "E2": 1.0 / S[1, 1],
            "G12": 1.0 / S[2, 2],
            "nu12": -S[0, 1] / S[0, 0],
        }
