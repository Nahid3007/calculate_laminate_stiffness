from dataclasses import dataclass
import numpy as np
from laminate.material import OrthotropicMaterial

# Laminate properties are based on
# REF: https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf

@dataclass
class Ply:
    material: OrthotropicMaterial
    thickness: float
    theta_deg: float
    z_bot: float = 0.0
    z_top: float = 0.0

    @property
    def lamina_stiffness_matrix(self) -> np.ndarray:
        """
        Transformed stiffness matrix Qbar according to Equation 21 of REF
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
