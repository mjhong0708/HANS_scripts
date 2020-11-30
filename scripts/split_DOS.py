#!/usr/bin/env python
from os import system, listdir

from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.electronic_structure.core import Spin, OrbitalType

import numpy as np
import pandas as pd

import argparse

parser = argparse.ArgumentParser(description="split DOS")
parser.add_argument("-p", default=False)
args = parser.parse_args()
polar = args.p


# dataframe object
DOS_df = pd.DataFrame()

# Make directory for DOS
path = "DOS_split"
if path not in listdir():
    system("mkdir {}".format(path))

# Load Vasprun object
dosrun = Vasprun("vasprun.xml")
tdos = dosrun.tdos
cdos = dosrun.complete_dos

# Get total DOS
E = tdos.energies - dosrun.efermi
DOS_df["E"] = E
E_F = dosrun.efermi  # not sure whether use or not
if dosrun.incar["ISPIN"] == 2:
    tdos_up = tdos.densities[Spin.up]
    tdos_down = tdos.densities[Spin.down]
    if polar:
        tdos_densities = [tdos_up, tdos_down]
        DOS_df["total_up"] = tdos_up
        DOS_df["total_down"] = tdos_down
        header_total = "E up down"
    else:
        tdos_densities = [tdos_up + tdos_down]
        DOS_df["total"] = tdos_densities[0]
        header_total = "E DOS"
else:
    tdos_densities = [tdos.densities]
    DOS_df["total"] = tdos_densities[0]
    header_total = "E DOS"


tdos_data = np.array([E] + tdos_densities).T
np.savetxt(f"{path}/DOS_total.dat", tdos_data, fmt="%.8f", header=header_total)

# Get projected DOS
sites = cdos.structure.sites
atom_names = [site.specie.value for i, site in enumerate(sites)]
atom_names_numbered = []

count = 1
for i in range(len(atom_names)):
    if i > 1 and atom_names[i - 1] != atom_names[i]:
        count = 1
    atom_names_numbered.append(atom_names[i] + str(count))
    count += 1

max_length = len(str(len(sites)))

orb_symbols = ["s", "p", "d", "f"]
for i, site in enumerate(sites):
    pdos_site = cdos.get_site_spd_dos(site).values()
    if dosrun.incar["ISPIN"] == 2:
        if polar:
            pdos_data = [E] + [
                item.densities[spin]
                for item in pdos_site
                for spin in [Spin.up, Spin.down]
            ]
            for j, (pdos_spd_up, pdos_spd_down) in enumerate(
                zip(pdos_data[1::2], pdos_data[2::2])
            ):
                DOS_df[f"{atom_names_numbered[i]}_{orb_symbols[j]}_up"] = pdos_spd_up
                DOS_df[
                    f"{atom_names_numbered[i]}_{orb_symbols[j]}_down"
                ] = pdos_spd_down
            header_proj = "E s_up s_down p_up p_down..."
        else:
            pdos_data = [E] + [
                item.densities[Spin.up] + item.densities[Spin.down]
                for item in pdos_site
            ]
            for j, pdos_spd in enumerate(pdos_data[1:]):
                DOS_df[f"{atom_names_numbered[i]}_{orb_symbols[j]}"] = pdos_spd
            header_proj = "E s p..."
    else:
        pdos_data = [E] + [
            item.densities for item in pdos_site for spin in [Spin.up, Spin.down]
        ]
        for j, pdos_spd in enumerate(pdos_data[1:]):
            DOS_df[f"{atom_names_numbered[i]}_{orb_symbols[j]}"] = pdos_spd
        header_proj = "E s p..."

    pdos_data = np.array(pdos_data).T
    pdos_filename = f"DOS{str(i+1).rjust(max_length,'0')}_{atom_names_numbered[i]}.dat"
    np.savetxt(f"{path}/{pdos_filename}", pdos_data, header=header_proj, fmt="%.8f")

DOS_df.to_csv(path + "/DOS_all.csv")

import pickle

with open(path + "/DOS_all.pkl", "wb") as f:
    pickle.dump(DOS_df, f)
