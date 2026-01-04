from dataclasses import dataclass
import numpy as np
from laminate.material import OrthotropicMaterial

@dataclass
class Ply:
    """
    Represents a single lamina (ply) in a composite laminate.

    Parameter
    ----------
    material : OrthotropicMaterial
        The material properties of the ply.
    thickness : float
        Thickness of the ply (in meters or consistent units).
    theta_deg : float
        Orientation angle of the ply in degrees relative to the laminate reference axis.
    z_bot : float, optional
        Z-coordinate of the bottom surface of the ply. Default is 0.0.
    z_top : float, optional
        Z-coordinate of the top surface of the ply. Default is 0.0.

    Attributes
    ----------
    lamina_stiffness_matrix : np.ndarray, shape (3, 3)
        Transformed stiffness matrix Q̅ (Qbar) of the ply in the global
        laminate axes. Computed according to classical lamination theory
        (Equation 21 of NASA TM 110235, 1995).
    
    Notes
    -----
    Laminate properties are based on NASA TM 110235 (1995):
    https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf
    """
    material: OrthotropicMaterial
    thickness: float
    theta_deg: float
    z_bot: float = 0.0
    z_top: float = 0.0

    @property
    def lamina_stiffness_matrix(self) -> np.ndarray:
        """
        Calculates the transformed stiffness matrix Q̅ for the ply.

        Returns
        -------
        np.ndarray, shape (3, 3)
            The ply stiffness matrix transformed to the laminate coordinate
            system, accounting for ply orientation (theta_deg).

        Notes
        -----
        The transformation is based on Equation 21 of NASA TM 110235.
        It considers the cosine and sine of the ply angle and uses the
        reduced stiffness matrix of the material (Q).
        """
        theta = np.deg2rad(self.theta_deg)
        m = np.cos(theta)
        n = np.sin(theta)

        Q = self.material.reduced_stiffness_matrix
        Q11, Q12, Q22, Q66 = Q[0, 0], Q[0, 1], Q[1, 1], Q[2, 2]

        Qbar = np.zeros((3, 3))

        Qbar[0, 0] = Q11*m**4 + Q22*n**4 + 2*(Q12 + 2*Q66)*m**2*n**2
        Qbar[1, 1] = Q11*n**4 + Q22*m**4 + 2*(Q12 + 2*Q66)*m**2*n**2
        Qbar[0, 1] = (Q11 + Q22 - 4*Q66)*m**2*n**2 + Q12*(m**4 + n**4)
        Qbar[1, 0] = Qbar[0, 1]

        Qbar[0, 2] = (Q11 - Q12 - 2*Q66)*m**3*n - (Q22 - Q12 - 2*Q66)*m*n**3
        Qbar[2, 0] = Qbar[0, 2]

        Qbar[1, 2] = (Q11 - Q12 - 2*Q66)*m*n**3 - (Q22 - Q12 - 2*Q66)*m**3*n
        Qbar[2, 1] = Qbar[1, 2]

        Qbar[2, 2] = (Q11 + Q22 - 2*Q12 - 2*Q66)*m**2*n**2 + Q66*(m**4 + n**4)

        return Qbar
