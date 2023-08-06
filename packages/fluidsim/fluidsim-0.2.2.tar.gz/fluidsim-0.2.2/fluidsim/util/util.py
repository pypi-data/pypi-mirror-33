"""Utilities for the numerical simulations (:mod:`fluidsim.util`)
=================================================================

.. autofunction:: load_sim_for_plot

.. autofunction:: load_state_phys_file

"""

from __future__ import division, print_function

from builtins import object
import os as _os
import glob as _glob
from copy import deepcopy as _deepcopy
import inspect

import numpy as _np
import h5py as _h5py

import operator as _operator
import numbers as _numbers

from importlib import import_module


import fluiddyn as fld

from fluiddyn.util import mpi

from fluidsim import path_dir_results, solvers

from fluidsim.base.params import (
    load_info_solver,
    load_params_simul,
    Parameters,
    merge_params,
    fix_old_params,
)


def available_solver_keys():
    """Inspects the subpackage `fluidsim.solvers` for all available
    solvers.

    Returns
    -------
    list

    """
    top = _os.path.split(inspect.getfile(solvers))[0]
    top = _os.path.abspath(top) + _os.sep
    keys = list()
    for dirpath, dirname, filenames in _os.walk(top):
        if "solver.py" in filenames:
            dirpath = _os.path.abspath(dirpath)
            key = dirpath.replace(top, "")
            key = key.replace(_os.sep, ".")
            keys.append(key)

    return sorted(keys)


def module_solver_from_key(key=None):
    """Return the string corresponding to a module solver."""
    key = key.lower()
    keys = available_solver_keys()

    if key in keys:
        part_path = key
    else:
        raise ValueError(
            "You have to give a proper solver key, name solver given: " + key
        )

    base_solvers = "fluidsim.solvers"
    module_solver = base_solvers + "." + part_path + ".solver"

    return module_solver


def import_module_solver_from_key(key=None):
    """Import and reload the solver.

    Parameters
    ----------

    key : str
        The short name of a solver.

    """
    return import_module(module_solver_from_key(key))


def get_dim_from_solver_key(key):
    """Try to guess the dimension from the solver key (via the operator name).

    """
    cls = import_simul_class_from_key(key)
    info = cls.InfoSolver()
    for dim in range(4):
        if str(dim) in info.classes.Operators.class_name:
            return str(dim)

    raise NotImplementedError(
        "Cannot deduce dimension of the solver from the name "
        + info.classes.Operators.class_name
    )


def import_simul_class_from_key(key):
    """Import and reload a simul class.

    Parameters
    ----------

    key : str
        The short name of a solver.

    """
    solver = import_module(module_solver_from_key(key))
    return solver.Simul


def pathdir_from_namedir(name_dir=None):
    """Return the path if a result directory."""
    if name_dir is None:
        return _os.getcwd()

    if name_dir[0] != "/" and name_dir[0] != "~":
        name_dir = path_dir_results + "/" + name_dir
    return _os.path.expanduser(name_dir)


class ModulesSolvers(dict):
    """Dictionary to gather imported solvers."""

    def __init__(self, names_solvers):
        for key in names_solvers:
            self[key] = import_module_solver_from_key(key)


def name_file_from_time_approx(path_dir, t_approx=None):
    """Return the file name whose time is the closest to the given time.

    """
    path_files = _glob.glob(path_dir + "/state_phys_t*")
    nb_files = len(path_files)
    if nb_files == 0 and mpi.rank == 0:
        raise ValueError("No state file in the dir\n" + path_dir)

    name_files = [_os.path.split(path)[-1] for path in path_files]
    if "state_phys_t=" in name_files[0]:
        ind_start_time = len("state_phys_t=")
    else:
        ind_start_time = len("state_phys_t")

    times = _np.empty([nb_files])
    for ii, name in enumerate(name_files):
        times[ii] = float(name[ind_start_time : ind_start_time + 7])
    if t_approx is None:
        t_approx = times.max()
    i_file = abs(times - t_approx).argmin()
    name_file = _os.path.split(path_files[i_file])[-1]
    return name_file


def load_sim_for_plot(path_dir=None, merge_missing_params=False):
    """Create a object Simul from a dir result.

    Creating simulation objects with this function should be fast because the
    state is not initialized with the output file and only a coarse operator is
    created.

    Parameters
    ----------

    path_dir : str (optional)

      Path of the directory of the simulation.

    merge_missing_params : bool (optional, default == False)

      Can be used to load old simulations carried out with an old fluidsim
      version.

    """
    path_dir = pathdir_from_namedir(path_dir)
    solver = _import_solver_from_path(path_dir)
    params = load_params_simul(path_dir=path_dir)

    if merge_missing_params:
        merge_params(params, solver.Simul.create_default_params())

    params.path_run = path_dir
    params.init_fields.type = "constant"
    params.init_fields.modif_after_init = False
    params.ONLY_COARSE_OPER = True
    params.NEW_DIR_RESULTS = False
    params.output.HAS_TO_SAVE = False
    params.output.ONLINE_PLOT_OK = False

    if params.forcing.type.startswith("in_script"):
        params.forcing.enable = False

    try:
        params.preprocess.enable = False
    except AttributeError:
        pass

    fix_old_params(params)

    sim = solver.Simul(params)
    return sim


def _import_solver_from_path(path_dir):
    info_solver = load_info_solver(path_dir=path_dir)
    solver = import_module(info_solver.module_name)
    return solver


def load_state_phys_file(
    name_dir=None,
    t_approx=None,
    modif_save_params=True,
    merge_missing_params=False,
):
    """Create a simulation from a file.

    For large resolution, creating a simulation object with this function can
    be slow because the state is initialized with the output file.

    Parameters
    ----------

    name_dir : str (optional)

      Name of the directory of the simulation. If nothing is given, we load the
      data in the current directory.

    t_approx : number (optional)

      Approximate time of the file to be loaded.

    modif_save_params :  bool (optional, default == True)

      If True, the parameters of the simulation are modified before loading::

        params.output.HAS_TO_SAVE = False
        params.output.ONLINE_PLOT_OK = False

    merge_missing_params : bool (optional, default == False)

      Can be used to load old simulations carried out with an old fluidsim
      version.

    """

    path_dir = pathdir_from_namedir(name_dir)

    solver = _import_solver_from_path(path_dir)

    # choose the file with the time closer to t_approx
    name_file = name_file_from_time_approx(path_dir, t_approx)
    path_file = _os.path.join(path_dir, name_file)

    with _h5py.File(path_file, "r") as f:
        params = Parameters(hdf5_object=f["info_simul"]["params"])

    if merge_missing_params:
        merge_params(params, solver.Simul.create_default_params())

    params.path_run = path_dir
    params.NEW_DIR_RESULTS = False
    if modif_save_params:
        params.output.HAS_TO_SAVE = False
        params.output.ONLINE_PLOT_OK = False
    params.init_fields.type = "from_file"
    params.init_fields.from_file.path = path_file
    params.init_fields.modif_after_init = False
    try:
        params.preprocess.enable = False
    except AttributeError:
        pass

    fix_old_params(params)

    sim = solver.Simul(params)
    return sim


def modif_resolution_all_dir(t_approx=None, coef_modif_resol=2, dir_base=None):
    """Save files with a modified resolution."""
    path_base = pathdir_from_namedir(dir_base)
    list_dir_results = _glob.glob(path_base + "/SE2D*")
    for path_dir in list_dir_results:
        modif_resolution_from_dir(
            name_dir=path_dir,
            t_approx=t_approx,
            coef_modif_resol=coef_modif_resol,
            PLOT=False,
        )


def modif_resolution_from_dir(
    name_dir=None, t_approx=None, coef_modif_resol=2, PLOT=True
):
    """Save a file with a modified resolution."""

    path_dir = pathdir_from_namedir(name_dir)

    solver = _import_solver_from_path(path_dir)

    sim = load_state_phys_file(name_dir, t_approx)

    params2 = _deepcopy(sim.params)
    params2.oper.nx = sim.params.oper.nx * coef_modif_resol
    params2.oper.ny = sim.params.oper.ny * coef_modif_resol
    params2.init_fields.type = "from_simul"

    sim2 = solver.Simul(params2)
    sim2.init_fields.get_state_from_simul(sim)

    print(sim2.params.path_run)

    sim2.output.path_run = path_dir + "/State_phys_{0}x{1}".format(
        sim2.params.oper.nx, sim2.params.oper.ny
    )
    print("Save file in directory\n" + sim2.output.path_run)
    sim2.output.phys_fields.save(particular_attr="modif_resolution")

    print("The new file is saved.")

    if PLOT:
        sim.output.phys_fields.plot(numfig=0)
        sim2.output.phys_fields.plot(numfig=1)
        fld.show()


def times_start_end_from_path(path):
    """Return the start and end times from a result directory path.

    """

    path_file = path + "/stdout.txt"
    if not _os.path.exists(path_file):
        print("Given path does not exist:\n " + path)
        return 666, 666

    with open(path_file, "r") as file_stdout:

        line = ""
        while not line.startswith("it ="):
            line = file_stdout.readline()

        words = line.split()
        t_s = float(words[6])

        # in order to get the informations at the end of the file,
        # we do not want to read the full file...
        file_stdout.seek(0, 2)  # go to the end
        nb_caract = file_stdout.tell()
        nb_caract_to_read = min(nb_caract, 1000)
        file_stdout.seek(-nb_caract_to_read, 2)
        while line != "":
            if line.startswith("it ="):
                line_it = line
            last_line = line
            line = file_stdout.readline()

        if last_line.startswith("save state_phys"):
            word = last_line.replace("=", " ").split()[-1]
            t_e = float(word.replace(".hd5", ""))
        else:
            words = line_it.split()
            t_e = float(words[6])

    # print('t_s = {0:.3f}, t_e = {1:.3f}'.format(t_s, t_e))

    return t_s, t_e


class SetOfDirResults(object):
    """Represent a set of result directories."""

    def __init__(self, arg):
        if isinstance(arg, str):
            dir_base = pathdir_from_namedir(arg)
            paths_results = _glob.glob(dir_base + "/SE2D_*")
            if len(paths_results) == 0:
                print("No result directory in the directory\n" + dir_base)
        else:
            paths_results = arg
            for ind, val in enumerate(arg):
                paths_results[ind] = pathdir_from_namedir(val)
            if len(paths_results) == 0:
                print("paths_results empty")

        self.nb_dirs = len(paths_results)

        self.dict_paths = {}
        self.dict_params = {}

        keys_values = ["c", "f", "name_solver", "nh"]
        self.dict_values = {}
        for k in keys_values:
            self.dict_values[k] = []

        for path_dir in paths_results:
            path_file = path_dir + "/param_simul.h5"

            name_run = _os.path.split(path_dir)[1]

            if not _os.path.exists(path_file):
                print(
                    "No file param_simul.h5 in dir\n"
                    + path_dir
                    + "This directory is skipped..."
                )
                self.nb_dirs -= 1
            else:
                self.dict_paths[name_run] = path_dir

                with _h5py.File(path_file, "r") as f:
                    name_run2 = f.attrs["name_run"]
                    name_solver = f.attrs["name_solver"]

                if name_run != name_run2:
                    raise ValueError("name_run != name_run2")

                # old code that have to be modified...
                params = Parameters(path_dir=path_dir, VERBOSE=False)
                self.dict_params[name_run] = params

                params.add_a_param("name_solver", name_solver)
                params.add_a_param("solver", name_solver)
                params.add_a_param("name_run", name_run)
                params.add_a_param("nh", params["nx"])

                if "c2" in params.__dict__ and "c" not in params.__dict__:
                    params.add_a_param("c", _np.sqrt(params["c2"]))

                for k in keys_values:
                    if not params[k] in self.dict_values[k]:
                        self.dict_values[k].append(params[k])

        if self.nb_dirs > 1:
            for k, v in self.dict_values.items():
                v.sort()
                if isinstance(v[0], _numbers.Number):
                    self.dict_values[k] = _np.array(v)

        self.paths = list(self.dict_paths.values())

    def dirs_from_values(self, k_sort="c2", **kwargs):
        """Return a list of dirs from conditions.

        >>> paths = setofdir.dirs_from_values2(
        >>>    c2=100, f=('>', 1), nh=('=',1920))

        """

        kdirs_corresp = list(self.dict_params.keys())
        for k, v in kwargs.items():
            if isinstance(v, tuple):
                str_operator = v[0]
                value = v[1]
            else:
                str_operator = "=="
                value = v

            if str_operator == "==":
                cond = _operator.eq
            elif str_operator == "!=":
                cond = _operator.ne
            elif str_operator == "<":
                cond = _operator.lt
            elif str_operator == ">":
                cond = _operator.gt
            elif str_operator == ">=":
                cond = _operator.le
            elif str_operator == "<=":
                cond = _operator.ge
            else:
                raise ValueError(
                    "Supports only the operators ==, !=, >, <, >=, <="
                )

            kdirs_corresp_temp = [
                kdir
                for kdir, params in self.dict_params.items()
                if cond(params[k], value)
            ]

            kdirs_corresp = list(
                set(kdirs_corresp).intersection(kdirs_corresp_temp)
            )

        if len(kdirs_corresp) == 0 and mpi.rank == 0:
            print("No result directory corresponds to the criteria.")

        kdirs_corresp.sort(key=lambda key: self.dict_params[key][k_sort])

        return kdirs_corresp

    def filter(self, **kwargs):
        """Return a filtered SetOfDirResults from conditions.

        >>> setofdir2 = setofdir.filter(c2=100, f=('>', 1), nh=('=',1920))
        """
        dirs = self.dirs_from_values(**kwargs)
        paths = [self.dict_paths[dir_i] for dir_i in dirs]
        return SetOfDirResults(paths)

    def path_larger_t_start(self):
        """Return the path corresponding to the run with larger *t_start*.

        """
        if len(self.paths) == 1:
            path = self.paths[0]
        else:
            t_s = -1.
            for path_temp in self.paths:
                t_s_temp, t_e = times_start_end_from_path(path_temp)
                if t_s_temp > t_s:
                    path = path_temp
                    t_s = t_s_temp
        return path

    def one_path_from_values(self, **kwargs):
        """Return one path from parameter values.

        If there are two corresponding runs, a warning is written and
        the function returns None.
        """
        keys_corresp = self.dirs_from_values(**kwargs)
        if len(keys_corresp) == 1:
            return self.dict_paths[keys_corresp[0]]

        elif len(keys_corresp) == 0:
            print("No directory corresponds to the given values.")
        elif len(keys_corresp) > 1:
            print("More than one directory corresponds to the given value(s).")
            paths = [self.dict_paths[dir_i] for dir_i in keys_corresp]
            sod = SetOfDirResults(paths)
            return sod.path_larger_t_start()
