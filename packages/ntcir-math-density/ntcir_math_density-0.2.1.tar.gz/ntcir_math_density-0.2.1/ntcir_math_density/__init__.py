"""
The NTCIR Math Density Estimator package uses datasets, and judgements in the NTCIR-11 Math-2, and
NTCIR-12 MathIR XHTML5 format to compute density, and probability estimates.
"""

from .estimator import get_judged_identifiers, get_all_positions, get_estimators # noqa:F401
from .estimator import get_estimates # noqa:F401
from .view import plot_estimates  # noqa:F401


__author__ = "Vit Novotny"
__version__ = "0.2.1"
__license__ = "MIT"
