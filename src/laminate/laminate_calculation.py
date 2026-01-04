import logging

from laminate.material import OrthotropicMaterial
from laminate.ply import Ply
from laminate.laminate import Laminate

def calculate_laminate_stiffness(basePath,
                                 laminate_inputs,
                                 logger=None):
    """
    Constructs a laminate from input properties, computes its ABD matrices,
    and logs homogenized membrane and bending engineering constants.

    Parameters
    ----------
    basePath : str or Path
        Base directory path for reference (currently unused, but can be used for
        file output or logging context).
    laminate_inputs : LaminateInput
        Input data for the laminate, including ply properties, thickness, and stacking angles.
    logger : logging.Logger, optional
        Logger to record calculation steps and results. If None, a default
        logger named "laminate_stiffness_analysis" is used.

    Returns
    -------
    None
        This function logs all results but does not return a value.

    Notes
    -----
    - Constructs an OrthotropicMaterial from the input properties.
    - Builds Ply objects for each angle in the stacking sequence.
    - Creates a Laminate instance, automatically computing A, B, and D matrices.
    - Logs A, B, D matrices and effective membrane and bending engineering constants.
    - Checks if the laminate is symmetric (B matrix ~ 0).
    """    
    if logger is None:
        logger = logging.getLogger("laminate_stiffness_analysis")
    
    material = OrthotropicMaterial(E1 = laminate_inputs.E1,
                                   E2 = laminate_inputs.E2,
                                   G12 = laminate_inputs.G12,
                                   nu12 = laminate_inputs.nu12
                                   )
    
    # Build plies
    plies = [Ply(material = material,
                 thickness = laminate_inputs.t_ply,
                 theta_deg = theta
                 )
        for theta in laminate_inputs.ply_angles
    ]

    # Laminate
    laminate = Laminate(plies)

    # Log results
    logger.info("A matrix:\n%s", laminate.A)
    if not laminate.is_symmetric:
        logger.info("Unsymmetric laminate detected (B matrix != 0).")
    logger.info("B matrix:\n%s", laminate.B)
    logger.info("D matrix:\n%s", laminate.D)

    logger.info("Homogenized membrane stiffness:\n%s",laminate.membrane_engineering_constants)
    logger.info("Homogenized bening stiffness:\n%s",laminate.bending_engineering_constants)

    logger.info("Laminate analysis complete")
    