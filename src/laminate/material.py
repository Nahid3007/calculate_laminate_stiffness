from dataclasses import dataclass
import numpy as np

# Laminate properties are based on
# REF: https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf

@dataclass(frozen=True)
class OrthotropicMaterial:
    E1: float
    E2: float
    G12: float
    nu12: float

    @property
    def nu21(self) -> float:
        """
        Equation 6 of REF
        """
        return self.nu12 * self.E2 / self.E1

    @property
    def reduced_stiffness_matrix(self) -> np.ndarray:
        """
        Reduced stiffness matrix Q according to equation 9 and 10 of REF
        """
        denom = 1.0 - self.nu12 * self.nu21

        Q11 = self.E1 / denom
        Q22 = self.E2 / denom
        Q12 = self.nu12 * self.E2 / denom
        Q66 = self.G12

        Q = np.array([
            [Q11, Q12, 0.0],
            [Q12, Q22, 0.0],
            [0.0, 0.0, Q66]
        ])

        return Q