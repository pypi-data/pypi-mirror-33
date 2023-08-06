"""Numerical simulations (:mod:`fluidsim`)
==========================================

.. _simul:

The package :mod:`fluidsim` provides an object-oriented toolkit for doing
numerical simulations of different equations (incompressible Navier-Stokes,
shallow-water, primitive equations, with and without the quasi-geostrophic limit,
adjoin equations, ...)  with different simple methods (pseudo-spectral, finite
differences) and geometries (1D, 2D and 3D periodic, 1 inhomogeneous direction,
...).

The package is organised in four sub-packages:

.. autosummary::
   :toctree:

   util
   base
   operators
   solvers
   magic

"""

from ._version import __version__

from fluiddyn.io import FLUIDSIM_PATH as path_dir_results

from .util.util import (
    import_module_solver_from_key,
    import_simul_class_from_key,
    load_sim_for_plot,
    load_state_phys_file,
    modif_resolution_from_dir,
    modif_resolution_all_dir,
)

# clean up
from . import util

del util


__all__ = [
    "__version__",
    "path_dir_results",
    "import_module_solver_from_key",
    "import_simul_class_from_key",
    "load_sim_for_plot",
    "load_state_phys_file",
    "modif_resolution_from_dir",
    "modif_resolution_all_dir",
]
