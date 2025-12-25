from pathlib import Path

from laminate.utilities import read_input, setup_logger
from laminate.material import OrthotropicMaterial
from laminate.ply import Ply
from laminate.laminate import Laminate

# Always resolve paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input.json"
LOG_FILE = BASE_DIR / "laminate_stiffness.log"


def main() -> None:
    logger = setup_logger("laminate", LOG_FILE)
    logger.info("Starting laminate analysis")

    # Read structured input (dataclass)
    inp = read_input(INPUT_FILE)

    logger.info(
    "Input data from JSON:\n"
    "E1 = %.3f, E2 = %.3f, G12 = %.3f, nu12 = %.3f\n"
    "Ply thickness = %.3f\n"
    "Stacking angles = %s\n"
    "Total stack thickness = %s",
    float(inp.E1),
    float(inp.E2),
    float(inp.G12),
    float(inp.nu12),
    float(inp.t_ply),
    inp.ply_angles,
    float(inp.t_ply)*len(inp.ply_angles))

    # Material
    material = OrthotropicMaterial(
        E1=inp.E1,
        E2=inp.E2,
        G12=inp.G12,
        nu12=inp.nu12,
    )

    # Build plies
    plies = [
        Ply(
            material=material,
            thickness=inp.t_ply,
            theta_deg=theta,
        )
        for theta in inp.ply_angles
    ]

    logger.info("Calcuate ABD matricies and homogenized stiffness properties")
    # Laminate
    laminate = Laminate(plies)

    # Log results
    logger.info("A matrix:\n%s", laminate.A)
    if not laminate.is_symmetric:
        logger.info("Unsymmetric laminate detected (B matrix != 0).")
    logger.info("B matrix:\n%s", laminate.B)
    logger.info("D matrix:\n%s", laminate.D)

    logger.info("Homogenized properties:\n%s", {k: float(v) for k, v in laminate.effective_properties.items()})

    logger.info("Laminate analysis complete")


if __name__ == "__main__":
    main()
