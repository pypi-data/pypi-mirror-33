from __future__ import division
from __future__ import print_function

from builtins import range
import numpy as np
import h5py

from fluiddyn.util import mpi

from fluidsim.base.output.spect_energy_budget import (
    SpectralEnergyBudgetBase,
    cumsum_inv,
    inner_prod,
)

from .normal_mode import NormalModeDecomposition, NormalModeDecompositionModified


class SpectralEnergyBudgetSW1LWaves(SpectralEnergyBudgetBase):
    """Save and plot spectra."""

    def __init__(self, output):

        params = output.sim.params
        self.c2 = params.c2
        self.f = params.f

        super(SpectralEnergyBudgetSW1LWaves, self).__init__(output)

    def compute(self):
        """compute spectral energy budget the one time."""
        oper = self.sim.oper

        # print_memory_usage('start function compute seb')

        ux = self.sim.state.state_phys.get_var("ux")
        uy = self.sim.state.state_phys.get_var("uy")
        eta = self.sim.state.state_phys.get_var("eta")
        h = 1. + eta

        Jx = h * ux
        Jy = h * uy
        Jx_fft = oper.fft2(Jx)
        Jy_fft = oper.fft2(Jy)
        del (Jx, Jy)

        get_var = self.sim.state.get_var
        ux_fft = get_var("ux_fft")
        uy_fft = get_var("uy_fft")
        eta_fft = get_var("eta_fft")
        h_fft = eta_fft.copy()
        if mpi.rank == 0:
            h_fft[0, 0] = 1.

        rot_fft = oper.rotfft_from_vecfft(ux_fft, uy_fft)
        urx_fft, ury_fft = oper.vecfft_from_rotfft(rot_fft)
        del (rot_fft)
        urx = oper.ifft2(urx_fft)
        ury = oper.ifft2(ury_fft)

        q_fft, div_fft, a_fft = self.oper.qdafft_from_uxuyetafft(
            ux_fft, uy_fft, eta_fft
        )

        # if self.params.f != 0:
        #     udx_fft, udy_fft = oper.vecfft_from_divfft(div_fft)
        #     ugx_fft, ugy_fft, etag_fft = \
        #         self.oper.uxuyetafft_from_qfft(q_fft)
        #     uax_fft, uay_fft, etaa_fft = \
        #         self.oper.uxuyetafft_from_afft(a_fft)
        #     del(a_fft)
        #     # velocity influenced by linear terms
        #     u_infl_lin_x = udx_fft + uax_fft
        #     u_infl_lin_y = udy_fft + uay_fft

        udx_fft, udy_fft = oper.vecfft_from_divfft(div_fft)
        udx = oper.ifft2(udx_fft)
        udy = oper.ifft2(udy_fft)
        div = oper.ifft2(div_fft)
        del (div_fft)

        # print_memory_usage('before starting computing fluxes')

        # compute flux of Charney PE
        Fq_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, q_fft)
        transferCPE_fft = inner_prod(q_fft, Fq_fft)
        del (q_fft, Fq_fft)
        transfer2D_CPE = self.spectrum2D_from_fft(transferCPE_fft)
        del (transferCPE_fft)

        #         print(
        # ('sum(transfer2D_CPE) = {0:9.4e} ; sum(abs(transfer2D_CPE)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_CPE),
        # np.sum(abs(transfer2D_CPE)))
        # )

        px_h_fft, py_h_fft = oper.gradfft_from_fft(eta_fft)
        px_h = oper.ifft2(px_h_fft)
        py_h = oper.ifft2(py_h_fft)

        F_rh = -urx * px_h - ury * py_h
        F_dh = -udx * px_h - udy * py_h - h * div / 2
        F_de = -udx * px_h - udy * py_h - eta * div / 2
        del (px_h, py_h)
        F_rh_fft = oper.fft2(F_rh)
        F_dh_fft = oper.fft2(F_dh)
        F_de_fft = oper.fft2(F_de)
        del (F_rh, F_dh, F_de)
        oper.dealiasing(F_rh_fft)
        oper.dealiasing(F_dh_fft)
        oper.dealiasing(F_de_fft)

        transferEAr_fft = self.c2 * inner_prod(h_fft, F_rh_fft)
        transferEPd_fft = self.c2 * inner_prod(h_fft, F_dh_fft)
        transferEAd_fft = self.c2 * inner_prod(eta_fft, F_de_fft)
        del (F_rh_fft, F_dh_fft, F_de_fft)

        transfer2D_EAr = self.spectrum2D_from_fft(transferEAr_fft)
        transfer2D_EPd = self.spectrum2D_from_fft(transferEPd_fft)
        transfer2D_EAd = self.spectrum2D_from_fft(transferEAd_fft)
        del (transferEAr_fft, transferEPd_fft, transferEAd_fft)

        # print_memory_usage('after transfer2D_EAr')

        #         print(
        # ('sum(transfer2D_EAr) = {0:9.4e} ; sum(abs(transfer2D_EAr)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_EAr),
        # np.sum(abs(transfer2D_EAr)))
        # )

        #         print(
        # ('sum(transfer2D_EAd) = {0:9.4e} ; sum(abs(transfer2D_EAd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_EAd),
        # np.sum(abs(transfer2D_EAd)))
        # )

        hdiv_fft = oper.fft2(h * div)
        convP_fft = self.c2 / 2. * inner_prod(h_fft, hdiv_fft)
        convP2D = self.spectrum2D_from_fft(convP_fft)
        del (convP_fft, h_fft, hdiv_fft)

        EP = self.c2 / 2 * h * h
        EP_fft = oper.fft2(EP)
        del (EP, h)
        px_EP_fft, py_EP_fft = oper.gradfft_from_fft(EP_fft)
        del (EP_fft)

        convK_fft = (
            1.
            / 2
            * (
                -inner_prod(ux_fft, px_EP_fft)
                - inner_prod(uy_fft, py_EP_fft)
                - self.c2 * inner_prod(Jx_fft, px_h_fft)
                - self.c2 * inner_prod(Jy_fft, py_h_fft)
            )
        )
        del (px_h_fft, py_h_fft, px_EP_fft, py_EP_fft)
        convK2D = self.spectrum2D_from_fft(convK_fft)
        del (convK_fft)

        # print_memory_usage('after convK2D')

        #         print(
        # ('sum(convP2D-convK2D)*deltak = {0:9.4e}, sum(convP2D)*deltak = {1:9.4e}'
        # ).format(
        # np.sum(convP2D-convK2D)*self.oper.deltak,
        # np.sum(convP2D)*self.oper.deltak
        # )
        # )

        #         print(
        # ('                                           sum(convK2D)*deltak = {0:9.4e}'
        # ).format(
        # np.sum(convK2D)*self.oper.deltak
        # )
        # )

        Fxrd_fft, Fxdd_fft = self.fnonlinfft_from_uruddivfunc(
            urx, ury, udx, udy, div, udx_fft, udx
        )
        Fyrd_fft, Fydd_fft = self.fnonlinfft_from_uruddivfunc(
            urx, ury, udx, udy, div, udy_fft, udy
        )
        Fxrr_fft, Fxdr_fft = self.fnonlinfft_from_uruddivfunc(
            urx, ury, udx, udy, div, urx_fft, urx
        )
        Fyrr_fft, Fydr_fft = self.fnonlinfft_from_uruddivfunc(
            urx, ury, udx, udy, div, ury_fft, ury
        )

        transferErrr_fft = inner_prod(urx_fft, Fxrr_fft) + inner_prod(
            ury_fft, Fyrr_fft
        )
        transfer2D_Errr = self.spectrum2D_from_fft(transferErrr_fft)
        del (transferErrr_fft)
        #         print(
        # ('sum(transfer2D_Errr) = {0:9.4e} ; sum(abs(transfer2D_Errr)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Errr),
        # np.sum(abs(transfer2D_Errr)))
        # )

        transferEdrd_fft = inner_prod(udx_fft, Fxrd_fft) + inner_prod(
            udy_fft, Fyrd_fft
        )
        transfer2D_Edrd = self.spectrum2D_from_fft(transferEdrd_fft)
        del (transferEdrd_fft)
        #         print(
        # ('sum(transfer2D_Edrd) = {0:9.4e} ; sum(abs(transfer2D_Edrd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Edrd),
        # np.sum(abs(transfer2D_Edrd)))
        # )
        Clfromqq = inner_prod(udx_fft, Fxrr_fft) + inner_prod(udy_fft, Fyrr_fft)
        transferEdrr_rrd_fft = (
            Clfromqq
            + inner_prod(urx_fft, Fxrd_fft)
            + inner_prod(ury_fft, Fyrd_fft)
        )
        Clfromqq = self.spectrum2D_from_fft(Clfromqq)
        transfer2D_Edrr_rrd = self.spectrum2D_from_fft(transferEdrr_rrd_fft)
        del (transferEdrr_rrd_fft)
        #         print(
        # ('sum(transfer2D_Edrr_rrd) = {0:9.4e} ; '
        # 'sum(abs(transfer2D_Edrr_rrd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Edrr_rrd),
        # np.sum(abs(transfer2D_Edrr_rrd)))
        # )

        transferErdr_fft = inner_prod(urx_fft, Fxdr_fft) + inner_prod(
            ury_fft, Fydr_fft
        )
        transfer2D_Erdr = self.spectrum2D_from_fft(transferErdr_fft)
        del (transferErdr_fft)
        #         print(
        # ('sum(transfer2D_Erdr) = {0:9.4e} ; sum(abs(transfer2D_Erdr)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Erdr),
        # np.sum(abs(transfer2D_Erdr)))
        # )

        transferEddd_fft = inner_prod(udx_fft, Fxdd_fft) + inner_prod(
            udy_fft, Fydd_fft
        )
        transfer2D_Eddd = self.spectrum2D_from_fft(transferEddd_fft)
        del (transferEddd_fft)
        #         print(
        # ('sum(transfer2D_Eddd) = {0:9.4e} ; sum(abs(transfer2D_Eddd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Eddd),
        # np.sum(abs(transfer2D_Eddd)))
        # )

        Cqfromll = inner_prod(urx_fft, Fxdd_fft) + inner_prod(ury_fft, Fydd_fft)
        transferEddr_rdd_fft = (
            Cqfromll
            + inner_prod(udx_fft, Fxdr_fft)
            + inner_prod(udy_fft, Fydr_fft)
        )

        Cqfromll = self.spectrum2D_from_fft(Cqfromll)
        transfer2D_Eddr_rdd = self.spectrum2D_from_fft(transferEddr_rdd_fft)
        del (transferEddr_rdd_fft)
        #         print(
        # ('sum(transfer2D_Eddr_rdd) = {0:9.4e} ; '
        # 'sum(abs(transfer2D_Eddr_rdd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Eddr_rdd),
        # np.sum(abs(transfer2D_Eddr_rdd)))
        # )

        Fx_ru_fft = Fxrr_fft + Fxrd_fft
        del (Fxrr_fft, Fxrd_fft)
        Fy_ru_fft = Fyrr_fft + Fyrd_fft
        del (Fyrr_fft, Fyrd_fft)
        Fx_du_fft = Fxdr_fft + Fxdd_fft
        del (Fxdr_fft, Fxdd_fft)
        Fy_du_fft = Fydr_fft + Fydd_fft
        del (Fydr_fft, Fydd_fft)

        # print_memory_usage('after Fy_du_fft')

        etaux = eta * ux
        etauy = eta * uy

        etaux_fft = oper.fft2(etaux)
        etauy_fft = oper.fft2(etauy)
        del (etaux, etauy)

        px_etaux_fft, py_etaux_fft = oper.gradfft_from_fft(etaux_fft)
        px_etauy_fft, py_etauy_fft = oper.gradfft_from_fft(etauy_fft)

        px_etaux = oper.ifft2(px_etaux_fft)
        del (px_etaux_fft)
        py_etaux = oper.ifft2(py_etaux_fft)
        del (py_etaux_fft)
        px_etauy = oper.ifft2(px_etauy_fft)
        del (px_etauy_fft)
        py_etauy = oper.ifft2(py_etauy_fft)
        del (py_etauy_fft)

        Fx_reu = -urx * px_etaux - ury * py_etaux
        Fx_reu_fft = oper.fft2(Fx_reu)
        del (Fx_reu)

        Fx_deu = -udx * px_etaux - udy * py_etaux - 0.5 * div * eta * ux
        del (px_etaux, py_etaux)
        Fx_deu_fft = oper.fft2(Fx_deu)
        del (Fx_deu)

        Fy_reu = -urx * px_etauy - ury * py_etauy
        Fy_reu_fft = oper.fft2(Fy_reu)
        del (Fy_reu)

        Fy_deu = -udx * px_etauy - udy * py_etauy - 0.5 * div * eta * uy
        del (px_etauy, py_etauy)
        Fy_deu_fft = oper.fft2(Fy_deu)
        del (Fy_deu)

        transferEureu_fft = 0.5 * (
            inner_prod(ux_fft, Fx_reu_fft)
            + inner_prod(uy_fft, Fy_reu_fft)
            + inner_prod(etaux_fft, Fx_ru_fft)
            + inner_prod(etauy_fft, Fy_ru_fft)
        )
        del (Fx_reu_fft, Fy_reu_fft, Fx_ru_fft, Fy_ru_fft)

        transfer2D_Eureu = self.spectrum2D_from_fft(transferEureu_fft)
        #         print(
        # ('sum(transferEureu_fft) = {0:9.4e} ; '
        # 'sum(abs(transferEureu_fft)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Eureu),
        # np.sum(abs(transfer2D_Eureu)))
        # )

        transferEudeu_fft = 0.5 * (
            inner_prod(ux_fft, Fx_deu_fft)
            + inner_prod(uy_fft, Fy_deu_fft)
            + inner_prod(etaux_fft, Fx_du_fft)
            + inner_prod(etauy_fft, Fy_du_fft)
        )
        del (Fx_deu_fft, Fy_deu_fft, Fx_du_fft, Fy_du_fft)
        del (etaux_fft, etauy_fft)

        transfer2D_Eudeu = self.spectrum2D_from_fft(transferEudeu_fft)
        del (transferEudeu_fft)
        #         print(
        # ('sum(transferEudeu_fft) = {0:9.4e} ; '
        # 'sum(abs(transferEudeu_fft)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Eudeu),
        # np.sum(abs(transfer2D_Eudeu)))
        # )

        transfer2D_EKr = (
            transfer2D_Errr
            + transfer2D_Edrd
            + transfer2D_Edrr_rrd
            + transfer2D_Eureu
        )
        transfer2D_EKd = (
            transfer2D_Erdr
            + transfer2D_Eddd
            + transfer2D_Eddr_rdd
            + transfer2D_Eudeu
        )

        # print_memory_usage('end of function compute seb')

        dict_results = {
            "transfer2D_EAr": transfer2D_EAr,
            "transfer2D_EAd": transfer2D_EAd,
            "transfer2D_EPd": transfer2D_EPd,
            "transfer2D_EKr": transfer2D_EKr,
            "transfer2D_EKd": transfer2D_EKd,
            "transfer2D_Errr": transfer2D_Errr,
            "transfer2D_Edrd": transfer2D_Edrd,
            "Clfromqq": Clfromqq,
            "transfer2D_Edrr_rrd": transfer2D_Edrr_rrd,
            "transfer2D_Erdr": transfer2D_Erdr,
            "transfer2D_Eddd": transfer2D_Eddd,
            "Cqfromll": Cqfromll,
            "transfer2D_Eddr_rdd": transfer2D_Eddr_rdd,
            "transfer2D_Eureu": transfer2D_Eureu,
            "transfer2D_Eudeu": transfer2D_Eudeu,
            "convP2D": convP2D,
            "convK2D": convK2D,
            "transfer2D_CPE": transfer2D_CPE,
        }
        return dict_results

    def _online_plot_saving(self, dict_results):

        transfer2D_CPE = dict_results["transfer2D_CPE"]
        transfer2D_EKr = dict_results["transfer2D_EKr"]
        transfer2D_EKd = dict_results["transfer2D_EKd"]
        transfer2D_EK = transfer2D_EKr + transfer2D_EKd
        transfer2D_EAr = dict_results["transfer2D_EAr"]
        transfer2D_EAd = dict_results["transfer2D_EAd"]
        transfer2D_EA = transfer2D_EAr + transfer2D_EAd
        convP2D = dict_results["convP2D"]
        convK2D = dict_results["convK2D"]
        khE = self.oper.khE
        PiCPE = cumsum_inv(transfer2D_CPE) * self.oper.deltak
        PiEK = cumsum_inv(transfer2D_EK) * self.oper.deltak
        PiEA = cumsum_inv(transfer2D_EA) * self.oper.deltak
        PiEtot = PiEK + PiEA
        CCP = cumsum_inv(convP2D) * self.oper.deltak
        CCK = cumsum_inv(convK2D) * self.oper.deltak

        self.axe_a.plot(khE + khE[1], PiEK, "r")
        self.axe_a.plot(khE + khE[1], PiEA, "b")
        self.axe_a.plot(khE + khE[1], PiEtot, "k", linewidth=2)
        self.axe_a.plot(khE + khE[1], CCP, "y")
        self.axe_a.plot(khE + khE[1], CCK, "y--")

        self.axe_b.plot(khE + khE[1], PiCPE, "g")

    def plot(self, tmin=0, tmax=1000, delta_t=2):

        with h5py.File(self.path_file, "r") as h5file:

            dset_times = h5file["times"]
            times = dset_times[...]
            # nt = len(times)

            dset_khE = h5file["khE"]
            khE = dset_khE[...]

            dset_transfer2D_EKr = h5file["transfer2D_EKr"]
            dset_transfer2D_EKd = h5file["transfer2D_EKd"]
            dset_transfer2D_EAr = h5file["transfer2D_EAr"]
            dset_transfer2D_EAd = h5file["transfer2D_EAd"]
            dset_transfer2D_EPd = h5file["transfer2D_EPd"]
            dset_convP2D = h5file["convP2D"]
            dset_convK2D = h5file["convK2D"]
            dset_transfer2D_CPE = h5file["transfer2D_CPE"]

            delta_t_save = np.mean(times[1:] - times[0:-1])
            delta_i_plot = int(np.round(delta_t / delta_t_save))
            if delta_i_plot == 0 and delta_t != 0.:
                delta_i_plot = 1
            delta_t = delta_i_plot * delta_t_save

            imin_plot = np.argmin(abs(times - tmin))
            imax_plot = np.argmin(abs(times - tmax))

            tmin_plot = times[imin_plot]
            tmax_plot = times[imax_plot]

            to_print = "plot(tmin={0}, tmax={1}, delta_t={2:.2f})".format(
                tmin, tmax, delta_t
            )
            print(to_print)

            to_print = """plot fluxes 2D
    tmin = {0:8.6g} ; tmax = {1:8.6g} ; delta_t = {2:8.6g}
    imin = {3:8d} ; imax = {4:8d} ; delta_i = {5:8d}""".format(
                tmin_plot, tmax_plot, delta_t, imin_plot, imax_plot, delta_i_plot
            )
            print(to_print)

            x_left_axe = 0.12
            z_bottom_axe = 0.36
            width_axe = 0.85
            height_axe = 0.57

            size_axe = [x_left_axe, z_bottom_axe, width_axe, height_axe]
            fig, ax1 = self.output.figure_axe(size_axe=size_axe)
            ax1.set_xlabel("$k_h$")
            ax1.set_ylabel("transfers")
            title = (
                "energy flux, solver "
                + self.output.name_solver
                + ", nh = {0:5d}".format(self.nx)
                + ", c = {0:.4g}, f = {1:.4g}".format(np.sqrt(self.c2), self.f)
            )
            ax1.set_title(title)
            ax1.set_xscale("log")
            ax1.set_yscale("linear")

            khE = khE + 1

            if delta_t != 0.:
                for it in range(imin_plot, imax_plot, delta_i_plot):
                    transferEKr = dset_transfer2D_EKr[it]
                    transferEAr = dset_transfer2D_EAr[it]
                    PiEKr = cumsum_inv(transferEKr) * self.oper.deltak
                    PiEAr = cumsum_inv(transferEAr) * self.oper.deltak
                    PiE = PiEKr + PiEAr
                    ax1.plot(khE, PiE, "k", linewidth=1)

                    convK = dset_convK2D[it]
                    CCK = cumsum_inv(convK) * self.oper.deltak
                    ax1.plot(khE, CCK, "y", linewidth=1)

                    convP = dset_convP2D[it]
                    CCP = cumsum_inv(convP) * self.oper.deltak
                    ax1.plot(khE, CCP, "y--", linewidth=1)

            # print(convK.sum()*self.oper.deltak,
            #       convP.sum()*self.oper.deltak,
            #       CCP[0], CCK[0])

            transferEKr = dset_transfer2D_EKr[imin_plot:imax_plot].mean(0)
            transferEKd = dset_transfer2D_EKd[imin_plot:imax_plot].mean(0)
            transferEAr = dset_transfer2D_EAr[imin_plot:imax_plot].mean(0)
            transferEAd = dset_transfer2D_EAd[imin_plot:imax_plot].mean(0)
            transferEPd = dset_transfer2D_EPd[imin_plot:imax_plot].mean(0)

            PiEKr = cumsum_inv(transferEKr) * self.oper.deltak
            PiEKd = cumsum_inv(transferEKd) * self.oper.deltak
            PiEAr = cumsum_inv(transferEAr) * self.oper.deltak
            PiEAd = cumsum_inv(transferEAd) * self.oper.deltak
            PiEPd = cumsum_inv(transferEPd) * self.oper.deltak

            PiEK = PiEKr + PiEKd
            PiEA = PiEAr + PiEAd
            PiE = PiEK + PiEA

            ax1.plot(khE, PiE, "k", linewidth=2)
            ax1.plot(khE, PiEK, "r", linewidth=2)
            ax1.plot(khE, PiEA, "b", linewidth=2)

            ax1.plot(khE, PiEKr, "r--", linewidth=2)
            ax1.plot(khE, PiEKd, "r:", linewidth=2)

            ax1.plot(khE, PiEAr, "b--", linewidth=2)
            ax1.plot(khE, PiEAd, "b:", linewidth=2)
            ax1.plot(khE, PiEPd, "c:", linewidth=1)

            convP = dset_convP2D[imin_plot:imax_plot].mean(0)
            convK = dset_convK2D[imin_plot:imax_plot].mean(0)

            CCP = cumsum_inv(convP) * self.oper.deltak
            CCK = cumsum_inv(convK) * self.oper.deltak

            ax1.plot(khE, CCP, "y--", linewidth=2)
            ax1.plot(khE, CCK, "y", linewidth=2)

            #         print(convK.sum()*self.oper.deltak,
            #               convP.sum()*self.oper.deltak,
            #               CCP[0], CCK[0],
            #               CCP[1], CCK[1]
            # )

            dset_transfer2D_Errr = h5file["transfer2D_Errr"]
            dset_transfer2D_Edrd = h5file["transfer2D_Edrd"]
            dset_transfer2D_Edrr_rrd = h5file["transfer2D_Edrr_rrd"]

            transferEdrr_rrd = dset_transfer2D_Edrr_rrd[imin_plot:imax_plot].mean(
                0
            )
            transferErrr = dset_transfer2D_Errr[imin_plot:imax_plot].mean(0)
            transferEdrd = dset_transfer2D_Edrd[imin_plot:imax_plot].mean(0)

            Pi_drr_rrd = cumsum_inv(transferEdrr_rrd) * self.oper.deltak
            Pi_rrr = cumsum_inv(transferErrr) * self.oper.deltak
            Pi_drd = cumsum_inv(transferEdrd) * self.oper.deltak

            ax1.plot(khE, Pi_drr_rrd, "m:", linewidth=1)
            ax1.plot(khE, Pi_rrr, "m--", linewidth=1)
            ax1.plot(khE, Pi_drd, "m-.", linewidth=1)

            dset_transfer2D_Eddd = h5file["transfer2D_Eddd"]
            dset_transfer2D_Erdr = h5file["transfer2D_Erdr"]
            dset_transfer2D_Eddr_rdd = h5file["transfer2D_Eddr_rdd"]
            dset_transfer2D_Eudeu = h5file["transfer2D_Eudeu"]

            transferEddr_rdd = dset_transfer2D_Eddr_rdd[imin_plot:imax_plot].mean(
                0
            )
            transferEddd = dset_transfer2D_Eddd[imin_plot:imax_plot].mean(0)
            transferErdr = dset_transfer2D_Erdr[imin_plot:imax_plot].mean(0)

            transferEudeu = dset_transfer2D_Eudeu[imin_plot:imax_plot].mean(0)

            Pi_ddr_rdd = cumsum_inv(transferEddr_rdd) * self.oper.deltak
            Pi_ddd = cumsum_inv(transferEddd) * self.oper.deltak
            Pi_rdr = cumsum_inv(transferErdr) * self.oper.deltak

            Pi_udeu = cumsum_inv(transferEudeu) * self.oper.deltak

            ax1.plot(khE, Pi_ddr_rdd, "c:", linewidth=1)
            ax1.plot(khE, Pi_ddd, "c--", linewidth=1)
            ax1.plot(khE, Pi_rdr, "c-.", linewidth=1)

            ax1.plot(khE, Pi_udeu, "g", linewidth=1)

            z_bottom_axe = 0.07
            height_axe = 0.17
            size_axe[1] = z_bottom_axe
            size_axe[3] = height_axe
            ax2 = fig.add_axes(size_axe)
            ax2.set_xlabel("$k_h$")
            ax2.set_ylabel("transfers")
            title = "Charney PE flux"
            ax2.set_title(title)
            ax2.set_xscale("log")
            ax2.set_yscale("linear")

            if delta_t != 0.:
                for it in range(imin_plot, imax_plot + 1, delta_i_plot):
                    transferCPE = dset_transfer2D_CPE[it]
                    PiCPE = cumsum_inv(transferCPE) * self.oper.deltak
                    ax2.plot(khE, PiCPE, "g", linewidth=1)

            transferCPE = dset_transfer2D_CPE[imin_plot:imax_plot].mean(0)
            PiCPE = cumsum_inv(transferCPE) * self.oper.deltak

        ax2.plot(khE, PiCPE, "m", linewidth=2)

    def _checksum_stdout(self, debug=False, **kwargs):
        if debug is True:
            for key, value in list(kwargs.items()):
                if mpi.nb_proc > 1:
                    value_g = mpi.comm.gather(value, root=0)
                else:
                    value_g = value

                if mpi.rank == 0:
                    print(
                        ("sum({0}) = {1:9.4e} ; sum(|{0}|) = {2:9.4e}").format(
                            key, np.sum(value_g), np.sum(np.abs(value_g))
                        )
                    )


class SpectralEnergyBudgetMSW1L(SpectralEnergyBudgetSW1LWaves):
    """Save and plot spectra."""

    def compute(self):
        """compute spectral energy budget the one time."""
        oper = self.sim.oper

        try:
            state_spect = self.sim.state.state_spect
            ux_fft = state_spect.get_var("ux_fft")
            uy_fft = state_spect.get_var("uy_fft")
            eta_fft = state_spect.get_var("eta_fft")
        except ValueError:
            state = self.sim.state
            ux_fft = state.get_var("ux_fft")
            uy_fft = state.get_var("uy_fft")
            eta_fft = state.get_var("eta_fft")

        rot_fft = oper.rotfft_from_vecfft(ux_fft, uy_fft)
        urx_fft, ury_fft = oper.vecfft_from_rotfft(rot_fft)
        del (rot_fft)
        urx = oper.ifft2(urx_fft)
        ury = oper.ifft2(ury_fft)

        q_fft, div_fft, a_fft = self.oper.qdafft_from_uxuyetafft(
            ux_fft, uy_fft, eta_fft
        )

        udx_fft, udy_fft = oper.vecfft_from_divfft(div_fft)

        if self.params.f != 0:
            ugx_fft, ugy_fft, etag_fft = self.oper.uxuyetafft_from_qfft(q_fft)
            uax_fft, uay_fft, etaa_fft = self.oper.uxuyetafft_from_afft(a_fft)
            # velocity influenced by linear terms
            # u_infl_lin_x = udx_fft + uax_fft
            # u_infl_lin_y = udy_fft + uay_fft

        # compute flux of Charney PE
        Fq_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, q_fft)

        transferCPE_fft = inner_prod(q_fft, Fq_fft)
        del (q_fft, Fq_fft)

        transfer2D_CPE = self.spectrum2D_from_fft(transferCPE_fft)
        del (transferCPE_fft)

        #         print(
        # ('sum(transfer2D_CPE) = {0:9.4e} ; sum(abs(transfer2D_CPE)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_CPE),
        # np.sum(abs(transfer2D_CPE)))
        # )

        Feta_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, eta_fft)
        transferEA_fft = self.c2 * inner_prod(eta_fft, Feta_fft)
        del (Feta_fft)
        transfer2D_EA = self.spectrum2D_from_fft(transferEA_fft)
        del (transferEA_fft)

        #         print(
        # ('sum(transfer2D_EA) = {0:9.4e} ; sum(abs(transfer2D_EA)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_EA),
        # np.sum(abs(transfer2D_EA)))
        # )

        convA_fft = self.c2 * inner_prod(eta_fft, div_fft)
        convA2D = self.spectrum2D_from_fft(convA_fft)
        del (convA_fft)

        Fxrr_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, urx_fft)
        Fyrr_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, ury_fft)

        Fxrd_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, udx_fft)
        Fyrd_fft = self.fnonlinfft_from_uxuy_funcfft(urx, ury, udy_fft)

        transferErrr_fft = inner_prod(urx_fft, Fxrr_fft) + inner_prod(
            ury_fft, Fyrr_fft
        )
        transfer2D_Errr = self.spectrum2D_from_fft(transferErrr_fft)
        del (transferErrr_fft)
        #         print(
        # ('sum(transfer2D_Errr) = {0:9.4e} ; sum(abs(transfer2D_Errr)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Errr),
        # np.sum(abs(transfer2D_Errr)))
        # )

        transferEdrd_fft = inner_prod(udx_fft, Fxrd_fft) + inner_prod(
            udy_fft, Fyrd_fft
        )
        transfer2D_Edrd = self.spectrum2D_from_fft(transferEdrd_fft)
        del (transferEdrd_fft)
        #         print(
        # ('sum(transfer2D_Edrd) = {0:9.4e} ; sum(abs(transfer2D_Edrd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Edrd),
        # np.sum(abs(transfer2D_Edrd)))
        # )

        Clfromqq = inner_prod(udx_fft, Fxrr_fft) + inner_prod(udy_fft, Fyrr_fft)
        transferEdrr_rrd_fft = (
            Clfromqq
            + inner_prod(urx_fft, Fxrd_fft)
            + inner_prod(ury_fft, Fyrd_fft)
        )
        Clfromqq = self.spectrum2D_from_fft(Clfromqq)
        transfer2D_Edrr_rrd = self.spectrum2D_from_fft(transferEdrr_rrd_fft)
        del (transferEdrr_rrd_fft)
        #         print(
        # ('sum(transfer2D_Edrr_rrd) = {0:9.4e} ; '
        # 'sum(abs(transfer2D_Edrr_rrd)) = {1:9.4e}'
        # ).format(
        # np.sum(transfer2D_Edrr_rrd),
        # np.sum(abs(transfer2D_Edrr_rrd)))
        # )

        transfer2D_EK = transfer2D_Errr + transfer2D_Edrd + transfer2D_Edrr_rrd
        dict_results = {
            "transfer2D_EK": transfer2D_EK,
            "transfer2D_Errr": transfer2D_Errr,
            "transfer2D_Edrd": transfer2D_Edrd,
            "Clfromqq": Clfromqq,
            "transfer2D_Edrr_rrd": transfer2D_Edrr_rrd,
            "transfer2D_EA": transfer2D_EA,
            "convA2D": convA2D,
            "transfer2D_CPE": transfer2D_CPE,
        }
        self._checksum_stdout(
            EK_GGG=transfer2D_Errr,
            EK_GGA=transfer2D_Edrr_rrd,
            EK_AAG=transfer2D_Edrd,
            EA=transfer2D_EA,
            Etot=transfer2D_EK + transfer2D_EA,
            debug=False,
        )
        return dict_results

    def _online_plot_saving(self, dict_results):

        transfer2D_CPE = dict_results["transfer2D_CPE"]
        transfer2D_EK = dict_results["transfer2D_EK"]
        transfer2D_EA = dict_results["transfer2D_EA"]
        convA2D = dict_results["convA2D"]
        khE = self.oper.khE
        PiCPE = cumsum_inv(transfer2D_CPE) * self.oper.deltak
        PiEK = cumsum_inv(transfer2D_EK) * self.oper.deltak
        PiEA = cumsum_inv(transfer2D_EA) * self.oper.deltak
        CCA = cumsum_inv(convA2D) * self.oper.deltak
        self.axe_a.plot(khE + khE[1], PiEK, "r")
        self.axe_a.plot(khE + khE[1], PiEA, "b")
        self.axe_a.plot(khE + khE[1], CCA, "y")
        self.axe_b.plot(khE + khE[1], PiCPE, "g")

    def plot(self, tmin=0, tmax=1000, delta_t=2):

        with h5py.File(self.path_file, "r") as h5file:

            dset_times = h5file["times"]
            dset_khE = h5file["khE"]
            khE = dset_khE[...]
            # khE = khE+khE[1]

            dset_transfer2D_EK = h5file["transfer2D_EK"]
            dset_transfer2D_Errr = h5file["transfer2D_Errr"]
            dset_transfer2D_Edrd = h5file["transfer2D_Edrd"]
            dset_transfer2D_Edrr_rrd = h5file["transfer2D_Edrr_rrd"]
            dset_transfer2D_EA = h5file["transfer2D_EA"]
            dset_convA2D = h5file["convA2D"]
            dset_transfer2D_CPE = h5file["transfer2D_CPE"]

            times = dset_times[...]
            # nt = len(times)

            delta_t_save = np.mean(times[1:] - times[0:-1])
            delta_i_plot = int(np.round(delta_t / delta_t_save))
            if delta_i_plot == 0 and delta_t != 0.:
                delta_i_plot = 1
            delta_t = delta_i_plot * delta_t_save

            imin_plot = np.argmin(abs(times - tmin))
            imax_plot = np.argmin(abs(times - tmax))

            tmin_plot = times[imin_plot]
            tmax_plot = times[imax_plot]

            to_print = "plot(tmin={0}, tmax={1}, delta_t={2:.2f})".format(
                tmin, tmax, delta_t
            )
            print(to_print)

            to_print = """plot fluxes 2D
    tmin = {0:8.6g} ; tmax = {1:8.6g} ; delta_t = {2:8.6g}
    imin = {3:8d} ; imax = {4:8d} ; delta_i = {5:8d}""".format(
                tmin_plot, tmax_plot, delta_t, imin_plot, imax_plot, delta_i_plot
            )
            print(to_print)

            x_left_axe = 0.12
            z_bottom_axe = 0.36
            width_axe = 0.85
            height_axe = 0.57

            size_axe = [x_left_axe, z_bottom_axe, width_axe, height_axe]
            fig, ax1 = self.output.figure_axe(size_axe=size_axe)
            ax1.set_xlabel("$k_h$")
            ax1.set_ylabel("transfers")
            title = (
                "energy flux, solver "
                + self.output.name_solver
                + ", nh = {0:5d}".format(self.nx)
                + ", c = {0:.4g}, f = {1:.4g}".format(np.sqrt(self.c2), self.f)
            )
            ax1.set_title(title)
            ax1.set_xscale("log")
            ax1.set_yscale("linear")

            if delta_t != 0.:
                for it in range(imin_plot, imax_plot, delta_i_plot):
                    transferEK = dset_transfer2D_EK[it]
                    transferEA = dset_transfer2D_EA[it]
                    PiEK = cumsum_inv(transferEK) * self.oper.deltak
                    PiEA = cumsum_inv(transferEA) * self.oper.deltak
                    PiE = PiEK + PiEA
                    ax1.plot(khE, PiE, "k", linewidth=1)

            transferEK = dset_transfer2D_EK[imin_plot:imax_plot].mean(0)
            transferEA = dset_transfer2D_EA[imin_plot:imax_plot].mean(0)
            PiEK = cumsum_inv(transferEK) * self.oper.deltak
            PiEA = cumsum_inv(transferEA) * self.oper.deltak
            PiE = PiEK + PiEA

            ax1.plot(khE, PiE, "k", linewidth=2)
            ax1.plot(khE, PiEK, "r", linewidth=2)
            ax1.plot(khE, PiEA, "b", linewidth=2)

            transferEdrr_rrd = dset_transfer2D_Edrr_rrd[imin_plot:imax_plot].mean(
                0
            )
            transferErrr = dset_transfer2D_Errr[imin_plot:imax_plot].mean(0)
            transferEdrd = dset_transfer2D_Edrd[imin_plot:imax_plot].mean(0)

            Pi_drr_rrd = cumsum_inv(transferEdrr_rrd) * self.oper.deltak
            Pi_rrr = cumsum_inv(transferErrr) * self.oper.deltak
            Pi_drd = cumsum_inv(transferEdrd) * self.oper.deltak

            ax1.plot(khE, Pi_drr_rrd, "m:", linewidth=1)
            ax1.plot(khE, Pi_rrr, "m--", linewidth=1)
            ax1.plot(khE, Pi_drd, "m-.", linewidth=1)

            convA2D = dset_convA2D[imin_plot:imax_plot].mean(0)
            CCA = cumsum_inv(convA2D) * self.oper.deltak

            ax1.plot(khE + khE[1], CCA, "y", linewidth=2)

            z_bottom_axe = 0.07
            height_axe = 0.17
            size_axe[1] = z_bottom_axe
            size_axe[3] = height_axe
            ax2 = fig.add_axes(size_axe)
            ax2.set_xlabel("$k_h$")
            ax2.set_ylabel("transfers")
            title = "Charney PE flux"
            ax2.set_title(title)
            ax2.set_xscale("log")
            ax2.set_yscale("linear")

            if delta_t != 0.:
                for it in range(imin_plot, imax_plot + 1, delta_i_plot):
                    transferCPE = dset_transfer2D_CPE[it]
                    PiCPE = cumsum_inv(transferCPE) * self.oper.deltak
                    ax2.plot(khE, PiCPE, "g", linewidth=1)

            transferCPE = dset_transfer2D_CPE[imin_plot:imax_plot].mean(0)
            PiCPE = cumsum_inv(transferCPE) * self.oper.deltak

        ax2.plot(khE, PiCPE, "m", linewidth=2)


class SpectralEnergyBudgetSW1L(SpectralEnergyBudgetSW1LWaves):
    def __init__(self, output, norm_mode=None):
        if norm_mode is None:
            self.norm_mode = NormalModeDecomposition(output)
        else:
            self.norm_mode = norm_mode

        super(SpectralEnergyBudgetSW1L, self).__init__(output)

    def _transfer_keys_coeff(self):
        c2 = self.params.c2
        # TODO: Check again for possible bugs as found in SpectralEnergyBudgetSW1LModified
        keys = {
            "uuu": ["ux_fft", "ux", "px_ux"],  # Quad. K.E. transfer terms
            "uvu": ["ux_fft", "uy", "py_ux"],
            "vuv": ["uy_fft", "ux", "px_uy"],
            "vvv": ["uy_fft", "uy", "py_uy"],
            "eeu": ["px_eta_fft", "eta", "ux"],  # Quad. A.P.E. transfer terms
            "eev": ["py_eta_fft", "eta", "uy"],
            "uud": [
                "ux_fft",
                "ux",
                "div",
            ],  # NonQuad. K.E. - Quad K.E. transfer terms
            "vvd": ["uy_fft", "uy", "div"],
            "dee": ["div_fft", "eta", "eta"],
        }  # NonQuad. K.E. - Quad A.P.E. transfer terms

        coeff = {
            "uuu": -1.,
            "uvu": -1.,
            "vuv": -1.,
            "vvv": -1.,
            "eeu": 0.5 * c2,
            "eev": 0.5 * c2,
            "uud": -0.5,
            "vvd": -0.5,
            "dee": 0.25 * c2,
        }

        return keys, coeff

    def compute(self):
        """Compute spectral energy budget once for current time."""

        oper = self.oper
        get_var = self.sim.state.get_var
        ux_fft = get_var("ux_fft")
        uy_fft = get_var("uy_fft")
        # eta_fft = get_var("eta_fft")
        c2 = self.params.c2

        ux = self.sim.state.state_phys.get_var("ux")
        uy = self.sim.state.state_phys.get_var("uy")
        eta = self.sim.state.state_phys.get_var("eta")

        Mx = eta * ux
        My = eta * uy
        Mx_fft = oper.fft2(Mx)
        My_fft = oper.fft2(My)
        oper.dealiasing(Mx_fft, My_fft)
        del (Mx, My)

        self.norm_mode.compute()

        Tq_keys, Tq_coeff = self._transfer_keys_coeff()

        Tq_terms = dict.fromkeys(Tq_keys)
        for key in list(Tq_keys.keys()):
            triad_key_modes, Tq_terms[key] = self.norm_mode.triad_from_keyfftphys(
                *Tq_keys[key]
            )

        Tq_fft = dict.fromkeys(triad_key_modes[0], 0.)
        n_modes = triad_key_modes[0].shape[0]
        for i in range(n_modes):  # GGG, GGA etc.
            k = triad_key_modes[0][i]
            for j in list(Tq_keys.keys()):  # uuu, uuv etc.
                Tq_fft[k] += np.real(Tq_coeff[j] * Tq_terms[j][i])

        del (Tq_keys, Tq_terms, Tq_coeff)

        # -------------------------
        # Quadratic exchange terms
        # -------------------------
        Cq_keys = {"ue": ["ux_fft", "px_eta_fft"], "ve": ["uy_fft", "py_eta_fft"]}
        Cq_terms = dict.fromkeys(Cq_keys)
        for key in list(Cq_keys.keys()):
            dyad_key_modes, Cq_terms[key] = self.norm_mode.dyad_from_keyfft(
                True, *Cq_keys[key]
            )

        Cq_coeff = {"ue": -c2, "ve": -c2}
        Cq_fft = dict.fromkeys(dyad_key_modes[0], 0.)
        n_modes = dyad_key_modes[0].shape[0]
        for i in range(n_modes):  # GG, AG, aG, AA
            k = dyad_key_modes[0][i]
            for j in list(Cq_keys.keys()):  # ue, ve
                Cq_fft[k] += np.real(Cq_coeff[j] * Cq_terms[j][i])

        del (Cq_keys, Cq_terms, Cq_coeff)

        # -----------------------------------------------
        # Non-quadratic K.E. transfer and exchange terms
        # -----------------------------------------------
        inner_prod = lambda a_fft, b_fft: a_fft.conj() * b_fft
        inner_prod2 = lambda a_fft, b_fft: a_fft * b_fft.conj()
        triple_prod_conv = lambda ax_fft, ay_fft, bx_fft, by_fft: (
            inner_prod(ax_fft, self.fnonlinfft_from_uxuy_funcfft(ux, uy, bx_fft))
            + inner_prod(
                ay_fft, self.fnonlinfft_from_uxuy_funcfft(ux, uy, by_fft)
            )
        )
        triple_prod_conv2 = lambda ax_fft, ay_fft, bx_fft, by_fft: (
            inner_prod2(ax_fft, self.fnonlinfft_from_uxuy_funcfft(ux, uy, bx_fft))
            + inner_prod2(
                ay_fft, self.fnonlinfft_from_uxuy_funcfft(ux, uy, by_fft)
            )
        )

        u_udM = triple_prod_conv(ux_fft, uy_fft, Mx_fft, My_fft)
        M_udu = triple_prod_conv2(Mx_fft, My_fft, ux_fft, uy_fft)
        divM = oper.ifft2(oper.divfft_from_vecfft(Mx_fft, My_fft))

        ux_divM = oper.fft2(ux * divM)
        uy_divM = oper.fft2(uy * divM)
        oper.dealiasing(ux_divM, uy_divM)

        u_u_divM = inner_prod(ux_fft, ux_divM) + inner_prod(uy_fft, uy_divM)
        Tnq_fft = 0.5 * np.real(M_udu + u_udM - u_u_divM)
        del (M_udu, u_udM, divM, ux_divM, uy_divM, u_u_divM)

        # --------------------------------------
        # Enstrophy transfer terms
        # --------------------------------------
        Tens_fft = oper.K2 * Tq_fft["GGG"]

        Tq_GGG = self.spectrum2D_from_fft(Tq_fft["GGG"])
        Tq_AGG = self.spectrum2D_from_fft(Tq_fft["AGG"])
        Tq_GAAs = self.spectrum2D_from_fft(Tq_fft["GAAs"])
        Tq_GAAd = self.spectrum2D_from_fft(Tq_fft["GAAd"])
        Tq_AAA = self.spectrum2D_from_fft(Tq_fft["AAA"])
        Tnq = self.spectrum2D_from_fft(Tnq_fft)
        Tens = self.spectrum2D_from_fft(Tens_fft)
        Cq_GG = self.spectrum2D_from_fft(Cq_fft["GG"])
        Cq_AG = self.spectrum2D_from_fft(Cq_fft["AG"])
        Cq_aG = self.spectrum2D_from_fft(Cq_fft["aG"])
        Cq_AA = self.spectrum2D_from_fft(Cq_fft["AA"])

        # Tq_TOT = Tq_GGG + Tq_AGG + Tq_GAAs + Tq_GAAd + Tq_AAA
        # self._checksum_stdout(
        #   GGG=Tq_GGG, GGA=Tq_AGG, AAG=(Tq_GAAs+Tq_GAAd), AAA=Tq_AAA,
        #   TNQ=Tnq, TOTAL=Tq_TOT, debug=True)

        dict_results = {
            "Tq_GGG": Tq_GGG,
            "Tq_AGG": Tq_AGG,
            "Tq_GAAs": Tq_GAAs,
            "Tq_GAAd": Tq_GAAd,
            "Tq_AAA": Tq_AAA,
            "Tnq": Tnq,
            "Cq_GG": Cq_GG,
            "Cq_AG": Cq_AG,
            "Cq_aG": Cq_aG,
            "Cq_AA": Cq_AA,
            "Tens": Tens,
        }

        return dict_results

    def _online_plot_saving(self, dict_results):

        # Tens = dict_results["Tens"]
        Tq_GGG = dict_results["Tq_GGG"]
        Tq_AGG = dict_results["Tq_AGG"]
        Tq_GAAs = dict_results["Tq_GAAs"]
        Tq_GAAd = dict_results["Tq_GAAd"]
        Tq_AAA = dict_results["Tq_AAA"]
        Tq_tot = Tq_GGG + Tq_AGG + Tq_GAAs + Tq_GAAd + Tq_AAA

        Cq_GG = dict_results["Cq_GG"]
        Cq_AG = dict_results["Cq_AG"] + dict_results["Cq_aG"]
        Cq_AA = dict_results["Cq_AA"]
        Cq_tot = Cq_GG + Cq_AG + Cq_AA

        khE = self.oper.khE
        # Piens = cumsum_inv(Tens) * self.oper.deltak
        Pi_tot = cumsum_inv(Tq_tot) * self.oper.deltak
        Pi_GGG = cumsum_inv(Tq_GGG) * self.oper.deltak
        Pi_AGG = cumsum_inv(Tq_AGG) * self.oper.deltak
        Pi_GAAs = cumsum_inv(Tq_GAAs) * self.oper.deltak
        Pi_GAAd = cumsum_inv(Tq_GAAd) * self.oper.deltak
        Pi_AAA = cumsum_inv(Tq_AAA) * self.oper.deltak

        Cflux_tot = cumsum_inv(Cq_tot) * self.oper.deltak
        Cflux_GG = cumsum_inv(Cq_GG) * self.oper.deltak
        Cflux_AG = cumsum_inv(Cq_AG) * self.oper.deltak
        Cflux_AA = cumsum_inv(Cq_AA) * self.oper.deltak

        self.axe_a.plot(
            khE + khE[1], Pi_tot, "k", linewidth=2, label=r"$\Pi_{tot}$"
        )
        self.axe_a.plot(
            khE + khE[1], Pi_GGG, "g--", linewidth=1, label=r"$\Pi_{GGG}$"
        )
        # self.axe_a.plot(
        #     khE+khE[1], Piens, 'g:', linewidth=1, label=r'$\Pi_{ens}$')
        self.axe_a.plot(
            khE + khE[1], Pi_AGG, "m--", linewidth=1, label=r"$\Pi_{GGA}$"
        )
        self.axe_a.plot(
            khE + khE[1], Pi_GAAs, "r:", linewidth=1, label=r"$\Pi_{G\pm\pm}$"
        )
        self.axe_a.plot(
            khE + khE[1], Pi_GAAd, "b:", linewidth=1, label=r"$\Pi_{G\pm\mp}$"
        )
        self.axe_a.plot(
            khE + khE[1], Pi_AAA, "y--", linewidth=1, label=r"$\Pi_{AAA}$"
        )

        self.axe_b.plot(
            khE + khE[1], Cflux_tot, "k", linewidth=2, label=r"$\Sigma C_{tot}$"
        )
        self.axe_b.plot(
            khE + khE[1], Cflux_GG, "g:", linewidth=1, label=r"$\Sigma C_{GG}$"
        )
        self.axe_b.plot(
            khE + khE[1], Cflux_AG, "m--", linewidth=1, label=r"$\Sigma C_{GA}$"
        )
        self.axe_b.plot(
            khE + khE[1], Cflux_AA, "y--", linewidth=1, label=r"$\Sigma C_{AA}$"
        )

        if self.nb_saved_times == 2:
            title = (
                "Spectral Energy Budget, solver "
                + self.output.name_solver
                + ", nh = {0:5d}".format(self.nx)
                + ", c = {0:.4g}, f = {1:.4g}".format(np.sqrt(self.c2), self.f)
            )
            self.axe_a.set_title(title)
            self.axe_a.legend()
            self.axe_b.legend()
            self.axe_b.set_ylabel(r"$\Sigma C(k_h)$")

    def plot(self, tmin=0, tmax=1000, delta_t=2):

        with h5py.File(self.path_file, "r") as h5file:

            dset_times = h5file["times"]
            dset_khE = h5file["khE"]
            khE = dset_khE[...] + 0.1  # Offset for semilog plots
            times = dset_times[...]

            delta_t_save = np.mean(times[1:] - times[0:-1])
            delta_i_plot = int(np.round(delta_t / delta_t_save))
            if delta_i_plot == 0 and delta_t != 0.:
                delta_i_plot = 1
            delta_t = delta_i_plot * delta_t_save

            imin_plot = np.argmin(abs(times - tmin))
            imax_plot = np.argmin(abs(times - tmax))

            tmin_plot = times[imin_plot]
            tmax_plot = times[imax_plot]

            to_print = "plot(tmin={0}, tmax={1}, delta_t={2:.2f})".format(
                tmin, tmax, delta_t
            )
            print(to_print)

            to_print = "plot fluxes 2D" + (
                ", tmin = {0:8.6g} ; tmax = {1:8.6g} ; delta_t = {2:8.6g}"
                + ", imin = {3:8d} ; imax = {4:8d} ; delta_i = {5:8d}"
            ).format(
                tmin_plot, tmax_plot, delta_t, imin_plot, imax_plot, delta_i_plot
            )
            print(to_print)

            # -------------------------
            #  Transfer terms
            # -------------------------
            x_left_axe = 0.12
            z_bottom_axe = 0.46
            width_axe = 0.85
            height_axe = 0.47
            size_axe = [x_left_axe, z_bottom_axe, width_axe, height_axe]
            fig1, ax1 = self.output.figure_axe(size_axe=size_axe)
            fig2, ax2 = self.output.figure_axe(size_axe=size_axe)

            ax1.set_xlabel("$k_h$")
            ax1.set_ylabel(r"Transfer fluxes, $\Pi(k_h)$")

            z_bottom_axe = 0.07
            height_axe = 0.27
            size_axe[1] = z_bottom_axe
            size_axe[3] = height_axe
            ax11 = fig1.add_axes(size_axe)
            ax11.set_xlabel("$k_h$")
            ax11.set_ylabel("Transfer terms, $T(k_h)$")

            title = (
                "Spectral Energy Budget, solver "
                + self.output.name_solver
                + ", nh = {0:5d}".format(self.nx)
                + ", c = {0:.4g}, f = {1:.4g}".format(np.sqrt(self.c2), self.f)
            )
            ax1.set_title(title)
            ax1.set_xscale("log")
            ax1.axhline()
            ax11.set_title(title)
            ax11.set_xscale("log")
            ax11.axhline()

            P = self.sim.params.forcing.forcing_rate
            norm = 1 if P == 0 else P
            if delta_t != 0.:
                for it in range(imin_plot, imax_plot, delta_i_plot):
                    transferEtot = 0.
                    for key in ["GGG", "AGG", "GAAs", "GAAd", "AAA"]:
                        transferEtot += h5file["Tq_" + key][it]
                    PiEtot = cumsum_inv(transferEtot) * self.oper.deltak / norm
                    ax1.plot(khE, PiEtot, "k", linewidth=1)

            Tq_GGG = h5file["Tq_GGG"][imin_plot:imax_plot].mean(0) / norm
            Tq_AGG = h5file["Tq_AGG"][imin_plot:imax_plot].mean(0) / norm
            Tq_GAAs = h5file["Tq_GAAs"][imin_plot:imax_plot].mean(0) / norm
            Tq_GAAd = h5file["Tq_GAAd"][imin_plot:imax_plot].mean(0) / norm
            Tq_AAA = h5file["Tq_AAA"][imin_plot:imax_plot].mean(0) / norm
            Tnq = h5file["Tnq"][imin_plot:imax_plot].mean(0) / norm
            Tens = h5file["Tens"][imin_plot:imax_plot].mean(0) / norm
            Tq_tot = Tq_GGG + Tq_AGG + Tq_GAAs + Tq_GAAd + Tq_AAA

            Pi_GGG = cumsum_inv(Tq_GGG) * self.oper.deltak
            Pi_AGG = cumsum_inv(Tq_AGG) * self.oper.deltak
            Pi_GAAs = cumsum_inv(Tq_GAAs) * self.oper.deltak
            Pi_GAAd = cumsum_inv(Tq_GAAd) * self.oper.deltak
            Pi_AAA = cumsum_inv(Tq_AAA) * self.oper.deltak
            Pi_nq = cumsum_inv(Tnq) * self.oper.deltak
            Pi_ens = cumsum_inv(Tens) * self.oper.deltak
            Pi_tot = Pi_GGG + Pi_AGG + Pi_GAAs + Pi_GAAd + Pi_AAA

            ax1.plot(khE, Pi_GGG, "g--", linewidth=2, label=r"$\Pi_{GGG}$")
            ax1.plot(khE, Pi_AGG, "m--", linewidth=2, label=r"$\Pi_{GGA}$")
            # ax1.plot(khE, Pi_GAAs, 'r:', linewidth=2, label=r'$\Pi_{G\pm\pm}$')
            # ax1.plot(khE, Pi_GAAd, 'b:', linewidth=2, label=r'$\Pi_{G\pm\mp}$')
            ax1.plot(
                khE, Pi_GAAs + Pi_GAAd, "r", linewidth=2, label=r"$\Pi_{GAA}$"
            )
            ax1.plot(khE, Pi_AAA, "y--", linewidth=2, label=r"$\Pi_{AAA}$")
            ax1.plot(khE, Pi_nq, "k--", linewidth=1, label=r"$\Pi^{NQ}$")
            ax1.plot(khE, Pi_tot, "k", linewidth=3, label=r"$\Pi_{tot}$")
            ax1.legend()

            ax11.plot(khE, Tq_GGG, "g--", linewidth=2, label=r"$T_{GGG}$")
            ax11.plot(khE, Tq_AGG, "m--", linewidth=2, label=r"$T_{GGA}$")
            ax11.plot(khE, Tq_GAAs, "r:", linewidth=2, label=r"$T_{G\pm\pm}$")
            ax11.plot(khE, Tq_GAAd, "b:", linewidth=2, label=r"$T_{G\pm\mp}$")
            ax11.plot(khE, Tq_AAA, "y--", linewidth=2, label=r"$T_{AAA}$")
            ax11.plot(khE, Tnq, "k--", linewidth=2, label=r"$T^{NQ}$")
            ax11.plot(khE, Tq_tot, "k", linewidth=3, label=r"$T_{tot}$")
            ax11.legend()
            # -------------------------
            # Quadratic exchange terms
            # -------------------------
            ax2.set_xlabel(r"$k_h$")
            ax2.set_ylabel(r"Exchange fluxes, $\Sigma C$")
            ax2.set_xscale("log")
            ax2.axhline()

            # .. TODO: Normalize with energy??
            exchange_GG = h5file["Cq_GG"][imin_plot:imax_plot].mean(0)
            exchange_AG = h5file["Cq_AG"][imin_plot:imax_plot].mean(0) + h5file[
                "Cq_aG"
            ][imin_plot:imax_plot].mean(0)
            exchange_AA = h5file["Cq_AA"][imin_plot:imax_plot].mean(0)
            exchange_mean = exchange_GG + exchange_AG + exchange_AA

            Cflux_GG = cumsum_inv(exchange_GG) * self.oper.deltak
            Cflux_AG = cumsum_inv(exchange_AG) * self.oper.deltak
            Cflux_AA = cumsum_inv(exchange_AA) * self.oper.deltak
            Cflux_mean = cumsum_inv(exchange_mean) * self.oper.deltak

            if delta_t != 0.:
                for it in range(imin_plot, imax_plot, delta_i_plot):
                    exchangetot = 0.
                    for key in ["GG", "AG", "aG", "AA"]:
                        exchangetot += h5file["Cq_" + key][it]
                    Cfluxtot = cumsum_inv(exchangetot) * self.oper.deltak
                    ax2.plot(khE, Cfluxtot, "k", linewidth=1)

        ax2.plot(khE, Cflux_mean, "k", linewidth=4, label=r"$\Sigma C_{tot}$")
        ax2.plot(khE, Cflux_GG, "g:", linewidth=2, label=r"$\Sigma C_{GG}$")
        ax2.plot(khE, Cflux_AG, "m--", linewidth=2, label=r"$\Sigma C_{GA}$")
        ax2.plot(khE, Cflux_AA, "y--", linewidth=2, label=r"$\Sigma C_{AA}$")
        ax2.legend()

        ax22 = fig2.add_axes(size_axe)
        ax22.set_xscale("log")
        ax22.axhline()
        ax22.set_xlabel(r"$k_h$")
        ax22.set_ylabel(r"$\Pi_{ens}(k_h)$")

        ax22.plot(khE, Pi_ens, "g", linewidth=3, label=r"$\Pi_{ens}$")
        ax22.legend()

        fig1.canvas.draw()
        fig2.canvas.draw()


class SpectralEnergyBudgetSW1LModified(SpectralEnergyBudgetSW1L):
    def __init__(self, output):
        norm_mode = NormalModeDecompositionModified(output)
        super(SpectralEnergyBudgetSW1LModified, self).__init__(output, norm_mode)

    def _transfer_keys_coeff(self):
        c2 = self.params.c2
        keys = {
            "uuu": ["ux_fft", "urx", "px_ux"],  # Quad. K.E. transfer terms
            "uvu": ["ux_fft", "ury", "py_ux"],
            "vuv": ["uy_fft", "urx", "px_uy"],
            "vvv": ["uy_fft", "ury", "py_uy"],
            "eeu": ["eta_fft", "urx", "px_eta"],  # Quad. A.P.E. transfer terms
            "eev": ["eta_fft", "ury", "py_eta"],
        }

        coeff = {
            "uuu": -1.,
            "uvu": -1.,
            "vuv": -1.,
            "vvv": -1.,
            "eeu": -c2,
            "eev": -c2,
        }

        return keys, coeff
