"""
Example Script for Composite Laminate Stiffness Calculation
===========================================================

This script demonstrates how to use the composite laminate module to:

1. Read laminate input properties from a YAML file.
2. Set up logging for the analysis.
3. Construct plies and laminates.
4. Compute ABD matrices and homogenized engineering constants.
5. Log all results.

Files
-----
input.yaml : YAML file containing laminate properties.

Usage
-----
Run this script as a standalone Python file.
"""

from pathlib import Path
import logging

from laminate.utilities import read_input, setup_logger, close_logger
from laminate.laminate_calculation import calculate_laminate_stiffness


BASE_PATH = Path(__file__).resolve().parent
INPUT_FILE = BASE_PATH / "input.yaml"

setup_logger(BASE_PATH/"laminate_stiffness_analysis.log")
logger = logging.getLogger("laminate_stiffness_analysis")
logger.setLevel("INFO")
logger.info("This is an example script!")

# read material inputs
laminate_inputs = read_input(INPUT_FILE)

# calculate laminate stiffness
calculate_laminate_stiffness(BASE_PATH, laminate_inputs)

close_logger(logger)