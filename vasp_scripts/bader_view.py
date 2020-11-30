#!/usr/bin/env python
from ase.visualize import view
from ase.io import read
import numpy as np
import pandas as pd


def mkCharge(filepath="./"):
    atoms = read(filepath + "CONTCAR")
    fileobj = open(filepath + "ACF.dat")
    sep = "---------------"
    i = 0  # Counter for the lines
    k = 0  # Counter of sep
    assume6columns = False
    charge_dict = {}
    nValenceE = dict.fromkeys(set([atom.symbol for atom in atoms]))
    for atom in list(nValenceE.keys()):
        nValenceE[atom] = int(
            input("Enter # of valence electrons for {} : ".format(atom))
        )

    for line in fileobj:
        if line[0] == "\n":  # check if there is an empty line in the
            i -= 1  # head of ACF.dat file
        if i == 0:
            headings = line
            if "BADER" in headings.split():
                j = headings.split().index("BADER")
            elif "CHARGE" in headings.split():
                j = headings.split().index("CHARGE")
            else:
                print(
                    'Can\'t find keyword "BADER" or "CHARGE".'
                    " Assuming the ACF.dat file has 6 columns."
                )
                j = 4
                assume6columns = True
        if sep in line:  # Stop at last separator line
            if k == 1:
                break
            k += 1
        if not i > 1:
            pass
        else:
            words = line.split()
            atom = atoms[int(words[0]) - 1]
            atomname = atom.symbol
            atom_charge = round(-float(words[j]) + nValenceE[atomname], 2)
            charge_dict["{}({})".format(i - 1, atomname)] = round(atom_charge, 2)
            atom.charge = atom_charge
        i += 1
    print(filepath)
    return charge_dict
