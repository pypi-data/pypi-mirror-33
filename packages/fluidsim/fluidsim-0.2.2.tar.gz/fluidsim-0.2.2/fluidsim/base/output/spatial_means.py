
from __future__ import division, print_function

import os
import numpy as np


from fluiddyn.util import mpi

from .base import SpecificOutput


def inner_prod(a_fft, b_fft):
    return np.real(a_fft.conj() * b_fft)


class SpatialMeansBase(SpecificOutput):
    """A :class:`SpatialMean` object handles the saving of .

    This class uses the particular functions defined by some solvers
    :func:`` and
    :func``. If the solver doesn't has these
    functions, this class does nothing.
    """

    _tag = "spatial_means"
    _name_file = _tag + ".txt"

    @staticmethod
    def _complete_params_with_default(params):
        tag = "spatial_means"

        params.output.periods_save._set_attrib(tag, 0)
        params.output._set_child(tag, attribs={"HAS_TO_PLOT_SAVED": False})

    def __init__(self, output):
        params = output.sim.params
        self.nx = params.oper.nx

        self.sum_wavenumbers = output.sum_wavenumbers
        try:
            self.vecfft_from_rotfft = output.oper.vecfft_from_rotfft
        except AttributeError:
            pass

        super(SpatialMeansBase, self).__init__(
            output,
            period_save=params.output.periods_save.spatial_means,
            has_to_plot_saved=params.output.spatial_means.HAS_TO_PLOT_SAVED,
        )

        if self.period_save != 0:
            self._save_one_time()

    def _init_files(self, dict_arrays_1time=None):

        if mpi.rank == 0:
            if not os.path.exists(self.path_file):
                self.file = open(self.path_file, "w")
            else:
                self.file = open(self.path_file, "r+")
                # to go to the end of the file
                self.file.seek(0, 2)

    def _online_save(self):
        self()

    def __call__(self):
        """Save the values at one time. """
        if self.sim.time_stepping.t - self.t_last_save >= self.period_save:
            self.t_last_save = self.sim.time_stepping.t
            self._save_one_time()

    def _save_one_time(self):
        self.t_last_save = self.sim.time_stepping.t

    def _init_online_plot(self):
        if mpi.rank == 0:
            width_axe = 0.85
            height_axe = 0.4
            x_left_axe = 0.12
            z_bottom_axe = 0.55

            size_axe = [x_left_axe, z_bottom_axe, width_axe, height_axe]
            fig, axe = self.output.figure_axe(size_axe=size_axe, numfig=3000000)
            self.axe_a = axe
            axe.set_xlabel("$t$")
            axe.set_ylabel("$E(t)$")
            title = (
                "mean quantities, solver "
                + self.output.name_solver
                + ", nh = {0:5d}".format(self.nx)
            )
            axe.set_title(title)

            z_bottom_axe = 0.08
            size_axe[1] = z_bottom_axe
            axe = fig.add_axes(size_axe)
            self.axe_b = axe
            axe.set_xlabel("$t$")
            axe.set_ylabel(r"$\epsilon(t)$")

    def load(self):
        dict_results = {}
        return dict_results

    def plot(self):
        pass

    def compute_time_means(self, tstatio=0., tmax=None):
        """compute the temporal means."""
        dict_results = self.load()
        if tmax is None:
            times = dict_results["t"]
            imax_mean = times.size - 1
            tmax = times[imax_mean]
        else:
            imax_mean = np.argmin(abs(times - tmax))
        imin_mean = np.argmin(abs(times - tstatio))

        dict_time_means = {}
        for key, value in dict_results.items():
            if isinstance(value, np.ndarray):
                dict_time_means[key] = np.mean(value[imin_mean : imax_mean + 1])
        return dict_time_means, dict_results

    def _close_file(self):
        try:
            self.file.close()
        except AttributeError:
            pass

    def time_first_saved(self):
        with open(self.path_file) as file_means:
            line = ""
            while not line.startswith("time ="):
                line = file_means.readline()

        words = line.split()
        return float(words[2])

    def time_last_saved(self):
        with open(self.path_file) as file_means:
            file_means.seek(0, 2)  # go to the end
            nb_caract = file_means.tell()
            nb_caract_to_read = min(nb_caract, 1000)
            file_means.seek(-nb_caract_to_read, 2)
            line = file_means.readline()
            while line != "":
                if line.startswith("time ="):
                    line_time = line
                line = file_means.readline()

        words = line_time.split()
        return float(words[2])
