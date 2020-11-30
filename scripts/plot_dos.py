#!/usr/bin/env python
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.electronic_structure.core import Spin, OrbitalType
from pymatgen.core.sites import PeriodicSite

import numpy as np
from scipy.signal._savitzky_golay import savgol_filter as savgol

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib.ticker

import argparse

parser = argparse.ArgumentParser(description="dos plot")
parser.add_argument("-a", nargs="+", type=str)
parser.add_argument("-Elim", default=[-6, 3], nargs="+", type=float)
parser.add_argument("-doslim", default=[-2, 2], nargs="+", type=float)
parser.add_argument("-p", default=False)
parser.add_argument("-o", default=None)
parser.add_argument("-smooth", default=0, type=int)
args = parser.parse_args()


class MyLocator(matplotlib.ticker.AutoMinorLocator):
    def __init__(self, n=2):
        super().__init__(n=n)


matplotlib.ticker.AutoMinorLocator = MyLocator


def figsize_in_cm(x, y):
    return (x / 2.54, y / 2.54)


# General font settings
mpl.rcParams["font.family"] = "Arial"
mpl.rcParams["font.size"] = 9
mpl.rcParams["mathtext.default"] = "regular"
mpl.rcParams["text.usetex"] = False

# Color settings
mpl.rcParams["axes.prop_cycle"] = cycler(color="krbgcmy")

# Figure properties
mpl.rcParams["figure.figsize"] = figsize_in_cm(8, 6)
mpl.rcParams["figure.dpi"] = 250

# Axes properties
mpl.rcParams["axes.linewidth"] = 1.25
mpl.rcParams["axes.labelsize"] = 10

# Ticks properties
mpl.rcParams["xtick.minor.visible"] = True
mpl.rcParams["ytick.minor.visible"] = True
mpl.rcParams["xtick.direction"] = "in"
mpl.rcParams["xtick.major.size"] = 4
mpl.rcParams["xtick.major.width"] = 1.25
mpl.rcParams["xtick.minor.size"] = 2
mpl.rcParams["xtick.minor.width"] = 1.25
mpl.rcParams["ytick.direction"] = "in"
mpl.rcParams["ytick.major.size"] = 4
mpl.rcParams["ytick.major.width"] = 1.25
mpl.rcParams["ytick.minor.size"] = 2
mpl.rcParams["ytick.minor.width"] = 1.25

# Legend properties
mpl.rcParams["legend.framealpha"] = 0
mpl.rcParams["legend.fontsize"] = 10

# plot setting
mpl.rcParams["lines.linewidth"] = 0.8
mpl.rcParams["lines.markersize"] = 3


def adj_avg(y, deg):
    size = len(y)
    smoothed = np.zeros(size)
    for i in range(deg):
        smoothed[i] = sum(y[: deg + i]) / (deg + i)
        smoothed[-1 - i] = sum(y[-1 - deg - i : -1]) / (deg + i)

    for i in range(deg, size - deg + 1):
        smoothed[i] = sum(y[i - deg : i + deg + 1]) / (deg * 2 + 1)
    return smoothed


def get_tdos(dosrun, spin_polar=False):
    tdos = dosrun.tdos.densities
    if spin_polar:
        return np.vstack((tdos[Spin.up], tdos[Spin.down]))
    else:
        return sum(tdos.values())


def get_pdos(dosrun, site, orbital, spin_polar=False):

    cdos = dosrun.complete_dos

    # Sites
    sites = cdos.structure.sites
    atom_names = [site.specie.value for i, site in enumerate(sites)]
    atom_names_number = []

    count = 1
    for i in range(len(atom_names)):
        if i > 1 and atom_names[i - 1] != atom_names[i]:
            count = 1
        atom_names_number.append(atom_names[i] + str(count))
        count += 1
    atom_names_number
    site_dict = dict(zip(atom_names_number, sites))

    # Orbitals
    orbital_symbols = ["s", "p", "d", "f"]
    orbital_dict = {}
    for i, orb in enumerate(cdos.get_spd_dos().keys()):
        orbital_dict[orbital_symbols[i]] = orb

    if spin_polar:
        pdos_densities_up = (
            cdos.get_site_spd_dos(site_dict[site])[orbital_dict[orbital]].densities
        )[Spin.up]
        pdos_densities_down = (
            cdos.get_site_spd_dos(site_dict[site])[orbital_dict[orbital]].densities
        )[Spin.down]
        return np.vstack((pdos_densities_up, pdos_densities_down))
    else:
        pdos_densities = sum(
            cdos.get_site_spd_dos(site_dict[site])[
                orbital_dict[orbital]
            ].densities.values()
        )
        return pdos_densities


def pdos_dataset(dosrun, sites_with_orbitals, spin_polar=False):
    dataset = {}
    dataset["E"] = dosrun.tdos.energies - dosrun.efermi

    site_orbital = [
        (item.split("_")[0], item.split("_")[1]) for item in sites_with_orbitals
    ]
    if spin_polar:
        for site, orbital in site_orbital:
            pdos_data = get_pdos(dosrun, site, orbital, spin_polar=True)
            dataset[f"{site}_{orbital}_up"] = pdos_data[0]
            dataset[f"{site}_{orbital}_down"] = pdos_data[1]
    else:
        for site, orbital in site_orbital:
            pdos_data = get_pdos(dosrun, site, orbital)
            dataset[f"{site}_{orbital}"] = pdos_data
    return dataset


def plot_tdos(
    dosrun,
    spin_polar=False,
    xlim=(-6, 3),
    ylim=(-8, 8),
    save=None,
    smooth=False,
    **kwargs,
):
    E = dosrun.tdos.energies - dosrun.efermi
    tdos_up = dosrun.tdos.densities[Spin.up]
    tdos_down = dosrun.tdos.densities[Spin.down]
    plt.figure(figsize=figsize_in_cm(9, 6.5))
    plt.xlabel("$E - E_F (eV)$")
    plt.ylabel("DOS")

    if spin_polar:
        if smooth:
            plt.plot(
                np.tile(E, 2),
                np.concatenate((adj_avg(tdos_up, smooth), adj_avg(-tdos_down, smooth))),
                **kwargs,
            )
        else:
            plt.plot(
                np.tile(E, 2), np.concatenate((tdos_up, -tdos_down)), **kwargs,
            )
    else:
        ylim = (0, ylim[1])
        if smooth:
            plt.plot(E, adj_avg(tdos_down + tdos_up, smooth), **kwargs)
        else:
            plt.plot(E, tdos_down + tdos_up, **kwargs)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.tight_layout()
    if save != None:
        plt.savefig(save, dpi=1000)
    plt.show()


def plot_pdos(
    dosrun,
    sites_with_orbitals,
    spin_polar=False,
    xlim=(-6, 3),
    ylim=(-2, 2),
    save=None,
    smooth=False,
    **kwargs,
):
    dataset = pdos_dataset(dosrun, sites_with_orbitals, spin_polar)
    plt.figure(figsize=figsize_in_cm(9, 6.5))
    plt.xlabel("$E - E_F (eV)$")
    plt.ylabel("DOS")
    if spin_polar:
        for key in list(dataset.keys())[1::2]:
            if smooth:
                plt.plot(
                    np.tile(dataset["E"], 2),
                    np.concatenate((dataset[key], -dataset[key[:-2]] + "down")),
                    label=key[:-3],
                    **kwargs,
                )
            else:
                plt.plot(
                    np.tile(dataset["E"], 2),
                    np.concatenate((dataset[key], -dataset[key[:-2]] + "down")),
                    label=key[:-3],
                    **kwargs,
                )
    else:
        for key in list(dataset.keys())[1:]:
            ylim = (0, ylim[1])
            if smooth:
                plt.plot(
                    dataset["E"], adj_avg(dataset[key], smooth), label=key, **kwargs
                )
            else:
                plt.plot(dataset["E"], dataset[key], label=key, **kwargs)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend(fontsize=8)
    plt.tight_layout()
    if save != None:
        plt.savefig(save, dpi=1000)
    plt.show()


if __name__ == "__main__":
    dosrun = Vasprun("vasprun.xml")
    if args.a[0] == "total":
        plot_tdos(
            dosrun,
            spin_polar=args.p,
            save=args.o,
            xlim=tuple(args.Elim),
            ylim=tuple(args.doslim),
            smooth=args.smooth,
        )
    else:
        plot_pdos(
            dosrun,
            args.a,
            spin_polar=args.p,
            save=args.o,
            xlim=tuple(args.Elim),
            ylim=tuple(args.doslim),
            smooth=args.smooth,
        )
