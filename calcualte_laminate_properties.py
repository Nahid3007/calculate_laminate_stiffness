import numpy as np

from utilities import (ply_stiffness,
                       transform_Q,
                       laminate_ABD,
                       homogenized_stiffness,
                       effective_properties,
                       effective_free_laminate,
                       read_input,
                       setup_logger)


# calculate laminate stiffness
def main_process():

    logger = setup_logger()

    logger.info("Calculate laminated stack stiffness properties")

    E11, E22, G12, nu12, t_ply, ply_angle_list = read_input("./inputs.json")

    # Log the inputs
    logger.info("Reading inputs")
    logger.info("Material stiffness properties: E11 = %s, E22 = %s, G12 = %s, nu12 = %s", E11, E22, G12, nu12)
    logger.info("Ply thickness: %s", t_ply)
    logger.info("Stacking angles: %s", ply_angle_list)
    logger.info("Done reading inputs")

    # number of total plies
    N = len(ply_angle_list)

    # total thickness
    total_thickness = N * t_ply
    logger.info(f"Number of plies: {N}, total tickness: {total_thickness}")


    Q = ply_stiffness(E11, E22, G12, nu12)

    z = np.linspace(-total_thickness / 2, total_thickness / 2, N + 1)

    plies = []
    for k in range(N):
        Qbar = transform_Q(Q, ply_angle_list[k])
        plies.append({
            "Qbar": Qbar,
            "z_bot": z[k],
            "z_top": z[k + 1]
        })

    logger.info("Calcualte ABD matricies and homogenized stiffness properties")
    A, B, D = laminate_ABD(plies)

    if np.allclose(B, 0.0, atol=1e-8):
        logger.info("Symmetric laminate detected")
        C_eff = homogenized_stiffness(A, total_thickness)
    else:
        C_eff = effective_free_laminate(A, B, D, total_thickness)

    np.set_printoptions(precision=2, suppress=True)

    logger.info("A matrix =\n%s", A)
    logger.info("B matrix =\n%s", B)
    logger.info("D matrix =\n%s", D)
    logger.info("Homogenized stiffness C_eff =\n%s", C_eff)

    E11_eff, E22_eff, G12_eff, nu12_eff = effective_properties(C_eff)

    logger.info("Homogenized properties: E11_eff = %.3f, E22_eff = %.3f, G12_eff = %.3f, nu12_eff = %.3f", E11_eff, E22_eff, G12_eff, nu12_eff)


if __name__ == '__main__':

    main_process()