from dataclasses import dataclass
import logging
import numpy as np

@dataclass(frozen=True)
class OrthotropicMaterial:
    """
    Represents an orthotropic lamina material with in-plane mechanical properties.

    Attributes
    ----------
    E1 : float
        Young's modulus in the principal material direction 1.
    E2 : float
        Young's modulus in the principal material direction 2.
    G12 : float
        In-plane shear modulus in the 1-2 plane.
    nu12 : float
        Major Poisson's ratio (strain in direction 2 due to stress in direction 1).

    Methods
    ----------
    nu21 : float
        Minor Poisson's ratio (strain in direction 1 due to stress in direction 2),
        computed as nu21 = nu12 * E2 / E1.
    reduced_stiffness_matrix : np.ndarray, shape (3, 3)
        Reduced stiffness matrix Q of the lamina in its principal material axes.
        Computed according to classical lamination theory (REF: NASA TM 110235, Eq. 9-10).

    Notes
    -----
    Lamina properties are based on NASA TM 110235 (1995):
    https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf
    """
    E1: float
    E2: float
    G12: float
    nu12: float

    def __post_init__(self):
        logger = logging.getLogger("laminate_stiffness_analysis")
        assert 0 < self.E1, logger.error(f"Moduli must be positive. E1 = {self.E1}")
        assert 0 < self.E2, logger.error(f"Moduli must be positive. E1 = {self.E2}")
        assert 0 < self.G12, logger.error(f"Moduli must be positive. E1 = {self.G12}")
        assert 0 < self.nu12, logger.error(f"Moduli must be positive. E1 = {self.nu12}")


    @property
    def nu21(self) -> float:
        """
        Minor Poisson's ratio in the 1-2 plane.

        Returns
        -------
        float
            nu21 = nu12 * E2 / E1
        """
        return self.nu12 * self.E2 / self.E1

    @property
    def reduced_stiffness_matrix(self) -> np.ndarray:
        """
        Reduced stiffness matrix of the lamina in its principal axes.

        Returns
        -------
        ndarray of shape (3, 3)
        The in-plane stiffness matrix ``Q``::

            [[Q11, Q12, 0],
             [Q12, Q22, 0],
             [0,   0,  Q66]]
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