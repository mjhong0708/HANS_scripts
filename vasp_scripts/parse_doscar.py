#!/usr/bin/env python
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import namedtuple
from openpyxl import Workbook
from openpyxl.styles.borders import Border, Side
from numba import jit
import mplSettings
from mplSettings import figsize_in_cm


def split_to_table(dat):
    table = []
    if type(dat) != list:
        dat = dat.split("\n")
        while "" in dat:
            dat.remove("")
    for item in dat:
        table.append(item.split())
    return np.array(table).astype(float).T


def lm_sum(pdos):
    if len(pdos) == 16:
        sum_indice = [1, 4, 9, 16]
    else:
        sum_indice = [1, 4, 9]
    ans = [pdos[0]]
    for i in range(len(sum_indice) - 1):
        ans.append(sum(pdos[sum_indice[i] : sum_indice[i + 1]]))
    return np.array(ans)


class Doscar:
    # @jit(nopython=True, cache=True)
    def __init__(self, filename="DOSCAR", poscar="POSCAR"):
        with open(poscar, "r") as f:
            lines = f.readlines()
            species = lines[5].split()
            numbers = [int(d) for d in lines[6].split()]
            atom_list = []
            for i, n in zip(species, numbers):
                for j in range(1, n + 1):
                    atom_list.append(f"{i}{j}")
            self.atoms = atom_list
        with open(filename, "r") as f:
            lines = f.readlines()
            separator = lines[5]
            dos_list = "".join(lines[6:]).split(separator)
            tdos_array = split_to_table(dos_list[0])[1:]
            pdos_arrays = [split_to_table(item)[1:] for item in dos_list[1:]]

            self.E_F = float(separator.split()[3])
            self.E = split_to_table(dos_list[0])[0] - float(separator.split()[3])

            spin_namedtuple = namedtuple("densities", ["u", "d"])
            self.tdos = spin_namedtuple(tdos_array[0], -tdos_array[1])
            pdos_up = [i[::2] for i in pdos_arrays]
            pdos_down = [-i[1::2] for i in pdos_arrays]

            pdos_up_lm_sum = [lm_sum(i) for i in pdos_up]
            pdos_down_lm_sum = [lm_sum(i) for i in pdos_down]
            try:
                pdos_orbitals = [
                    dict(
                        s=spin_namedtuple(
                            pdos_up_lm_sum[i][0, :], pdos_down_lm_sum[i][0, :]
                        ),
                        p=spin_namedtuple(
                            pdos_up_lm_sum[i][1, :], pdos_down_lm_sum[i][1, :]
                        ),
                        d=spin_namedtuple(
                            pdos_up_lm_sum[i][2, :], pdos_down_lm_sum[i][2, :]
                        ),
                        f=spin_namedtuple(
                            pdos_up_lm_sum[i][3, :], pdos_down_lm_sum[i][3, :]
                        ),
                    )
                    for i in range(len(pdos_up_lm_sum))
                ]
            except:
                pdos_orbitals = [
                    dict(
                        s=spin_namedtuple(
                            pdos_up_lm_sum[i][0, :], pdos_down_lm_sum[i][0, :]
                        ),
                        p=spin_namedtuple(
                            pdos_up_lm_sum[i][1, :], pdos_down_lm_sum[i][1, :]
                        ),
                        d=spin_namedtuple(
                            pdos_up_lm_sum[i][2, :], pdos_down_lm_sum[i][2, :]
                        ),
                    )
                    for i in range(len(pdos_up_lm_sum))
                ]

            self.pdos = dict(zip(atom_list, pdos_orbitals))

    def save_data(self, dest_filename="dos.xlsx", spin_polarized=True):
        wb = Workbook()
        ws_total = wb.active
        ws_total.title = "total"
        ws_total.append(["E", "up", "down"])
        for item in zip(self.E, self.tdos.u, self.tdos.d):
            ws_total.append(item)

        ws_partial = [wb.create_sheet(title=i) for i in self.atoms]
        for i, sheet in enumerate(ws_partial):
            sheet.append(
                ["E"]
                + [
                    "s_up",
                    "s_down",
                    "p_up",
                    "p_down",
                    "d_up",
                    "d_down",
                    "f_up",
                    "f_down",
                ]
            )
            partial_items = list(
                zip(
                    self.E,
                    list(self.pdos.values())[i]["s"][0],
                    list(self.pdos.values())[i]["s"][1],
                    list(self.pdos.values())[i]["p"][0],
                    list(self.pdos.values())[i]["p"][1],
                    list(self.pdos.values())[i]["d"][0],
                    list(self.pdos.values())[i]["d"][1],
                    list(self.pdos.values())[i]["f"][0],
                    list(self.pdos.values())[i]["f"][1],
                )
            )
            for item in partial_items:
                sheet.append(item)

        wb.save(filename=dest_filename)

    @staticmethod
    def plot_dos(E, dataset, labels, **kwargs):
        colors = ["k", "b", "r", "m", "g", "brown"]
        count = 0
        for data, label in zip(dataset, labels):
            if len(data) == 1:
                plt.plot(E, data[0], label=label, color=colors[count], **kwargs)
                count += 1
            else:
                plt.plot(E, data[0], color=colors[count], label=label, **kwargs)
                plt.plot(E, data[1], color=colors[count], **kwargs)
                count += 1

    def plot_tdos(self, Erange=None, dosrange=None, polar=True, save=None, **kwargs):
        fs = 20
        plt.figure(figsize=figsize_in_cm(9.5, 7))
        plt.title("Total")
        plt.xlabel("$E - E_F$")
        plt.ylabel("DOS")
        E = self.E
        if polar is True:
            dataset = [[self.tdos.u, self.tdos.d]]
        else:
            dataset = [[self.tdos.u - self.tdos.d]]
        self.plot_dos(E, dataset, ["total"])
        plt.legend(fontsize=7)
        if Erange != None:
            plt.xlim(Erange)
        if dosrange != None:
            plt.ylim(dosrange)
        plt.tight_layout()
        if save != None:
            plt.savefig("save" + ".png", dpi=1000)
        plt.show()

    def plot_pdos(
        self,
        atoms_with_orbitals,
        Erange=None,
        dosrange=None,
        polar=True,
        save=None,
        **kwargs,
    ):

        plt.figure(figsize=figsize_in_cm(9.5, 7))
        plt.title("Total")
        plt.xlabel("$E - E_F$")
        plt.ylabel("DOS")
        E = self.E
        selected_atoms = [i.split("_")[0] for i in atoms_with_orbitals]
        selected_orbitals = [i.split("_")[1] for i in atoms_with_orbitals]
        if polar is True:
            dataset = []
            for atom, orbital in zip(selected_atoms, selected_orbitals):
                dataset.append(self.pdos[atom][orbital])
        else:
            dataset = []
            for atom, orbital in zip(selected_atoms, selected_orbitals):
                dataset.append(
                    [self.pdos[atom][orbital].u - self.pdos[atom][orbital].d]
                )
        self.plot_dos(E, dataset, atoms_with_orbitals, **kwargs)
        plt.legend(fontsize=7)
        plt.tight_layout()

        if Erange != None:
            plt.xlim(Erange)
        if dosrange != None:
            plt.ylim(dosrange)
        if save != None:
            plt.savefig("save" + ".png", dpi=1000)
        plt.show()
