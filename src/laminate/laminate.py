from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from laminate.ply import Ply

@dataclass
class Laminate:
    """
    Represents a composite laminate composed of multiple plies and provides 
    methods to compute laminate stiffness and engineering constants.

    Attributes
    ----------
    plies : List[Ply]
        List of Ply objects defining the laminate stacking sequence.
    A : np.ndarray, shape (3, 3)
        Membrane stiffness matrix of the laminate.
    B : np.ndarray, shape (3, 3)
        Coupling stiffness matrix of the laminate.
    D : np.ndarray, shape (3, 3)
        Bending stiffness matrix of the laminate.

    Notes
    -----
    Laminate properties are based on NASA TM 110235 (1995):
    https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf
    """

    plies: List[Ply]
    A: np.ndarray = field(init=False)
    B: np.ndarray = field(init=False)
    D: np.ndarray = field(init=False)

    def __post_init__(self):
        self._assign_z_coordinates()
        self._compute_ABD()

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------
    @property
    def total_thickness(self) -> float:
        """
        Total thickness of the laminate.

        Returns
        -------
        float
            Sum of all ply thicknesses.
        """
        return sum(ply.thickness for ply in self.plies)

    def _assign_z_coordinates(self):
        """
        Assigns z-coordinate bounds to each ply in the laminate.

        Each ply receives `z_bot` and `z_top` attributes defining its
        bottom and top surface positions relative to the laminate mid-plane.
        """
        z = -self.total_thickness / 2.0
        for ply in self.plies:
            ply.z_bot = z
            z += ply.thickness
            ply.z_top = z

    # ------------------------------------------------------------------
    # ABD matrices
    # ------------------------------------------------------------------
    def _compute_ABD(self):
        """
        Computes the laminate stiffness matrices A, B, and D.

        A is the membrane stiffness matrix, B is the coupling matrix,
        and D is the bending stiffness matrix, computed using classical
        laminate theory from the stiffness of individual plies.
        """
        self.A = np.zeros((3, 3))
        self.B = np.zeros((3, 3))
        self.D = np.zeros((3, 3))

        for ply in self.plies:
            Qbar = ply.lamina_stiffness_matrix
            z0, z1 = ply.z_bot, ply.z_top

            self.A += Qbar * (z1 - z0)
            self.B += 0.5 * Qbar * (z1**2 - z0**2)
            self.D += (1.0 / 3.0) * Qbar * (z1**3 - z0**3)

    @property
    def is_symmetric(self) -> bool:
        """
        Checks whether the laminate is symmetric.

        Returns
        -------
        bool
            True if the coupling matrix B is approximately zero, indicating
            a symmetric laminate.
        """
        return np.allclose(self.B, 0.0, atol=1e-8)

    # ------------------------------------------------------------------
    # ABD compliance
    # ------------------------------------------------------------------
    def _abd(self) -> np.ndarray:
        """
        Constructs the full 6x6 ABD stiffness matrix.

        Returns
        -------
        np.ndarray, shape (6, 6)
            The combined ABD matrix of the laminate.
        """
        return np.block([[self.A, self.B],
                         [self.B, self.D]])

    def _abd_compliance(self) -> np.ndarray:
        """
        Computes the compliance matrix of the laminate.

        Returns
        -------
        np.ndarray, shape (6, 6)
            Inverse of the ABD stiffness matrix.
        """
        return np.linalg.inv(self._abd())

    # ------------------------------------------------------------------
    # Engineering constants extraction
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Membrane effective properties
    # ------------------------------------------------------------------
    @property
    def membrane_engineering_constants(self,
                                       ndigits: int | None = 3) -> Dict[str, float]:
        """
        Calculates effective in-plane engineering constants of the laminate.

        Parameters
        ----------
        ndigits : int or None, optional
            Number of decimal places to round the results to. If None,
            values are returned as full floats. Default is 3.

        Returns
        -------
        dict
            Dictionary containing:
            - 'E11': Longitudinal Young's modulus
            - 'E22': Transverse Young's modulus
            - 'G12': In-plane shear modulus
            - 'nu12': Major Poisson's ratio
        """
        h = self.total_thickness

        ABD_inv = self._abd_compliance()
        a = ABD_inv[:3, :3]
        
        props = {
            "E11": 1.0 / (a[0,0]*h),
            "E22": 1.0 / (a[1,1]*h),
            "G12": 1.0 / (a[2,2]*h),
            "nu12": -(a[0,1]*h) / (a[0,0]*h),
        }    

        if ndigits is not None:
            return {k: round(float(v), ndigits) for k, v in props.items()}
        
        return {k: float(v) for k, v in props.items()}

    # ------------------------------------------------------------------
    # Bending effective properties
    # ------------------------------------------------------------------
    @property
    def bending_engineering_constants(self,
                                      ndigits: int | None = 3) -> Dict[str, float]:
        """
        Calculates effective bending engineering constants of the laminate.

        Parameters
        ----------
        ndigits : int or None, optional
            Number of decimal places to round the results to. If None,
            values are returned as full floats. Default is 3.

        Returns
        -------
        dict
            Dictionary containing:
            - 'E11': Longitudinal bending modulus
            - 'E22': Transverse bending modulus
            - 'G12': In-plane bending shear modulus
            - 'nu12': Major Poisson's ratio in bending
        """
        h3 = self.total_thickness ** 3

        ABD_inv = self._abd_compliance()
        d = ABD_inv[3:, 3:]
        
        props = {
            "E11": 12.0 / (d[0,0]*h3),
            "E22": 12.0 / (d[1,1]*h3),
            "G12": 12.0 / (d[2,2]*h3),
            "nu12": -(d[0,1]*h3) / (d[0,0]*h3),
        }    

        if ndigits is not None:
            return {k: round(float(v), ndigits) for k, v in props.items()}
        
        return {k: float(v) for k, v in props.items()}

        

