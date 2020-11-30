#!/usr/bin/env python
import numpy as np
from pymatgen.io.vasp.outputs import Elfcar, Chgcar
import matplotlib.pyplot as plt
from ase.io import read
from ase.visualize import view


def find_closest_index(x, val):
    A = np.where(x <= val)
    return A[-1][-1]

def eval_chg(r, chg):
    n_a, n_b, n_c = chg.shape
    a = np.linspace(0,1,n_a)
    b = np.linspace(0,1,n_b)
    c = np.linspace(0,1,n_c)
    a_index = find_closest_index(a, r[0])
    b_index = find_closest_index(b, r[1])
    c_index = find_closest_index(c, r[2])
    return chg[a_index, b_index, c_index]

def eval_chg_path(r1, r2, filename, n_points=100):
    if filename == 'CHGCAR':
        chg = Chgcar.from_file("CHGCAR").data['total']
    elif filename == 'ELFCAR':
        chg = Elfcar.from_file("ELFCAR").data['total']
    
    path = np.array([r1 + (r2 - r1) * t for t in np.linspace(0, 1, n_points)])
    chg_path_output = []
    for r in path:
        chg_path_output.append(eval_chg(r, chg))
    return chg_path_output

def plot_chg_path(ax, r1, r2, filename, n_points=100):
    x = np.linspace(0,1,n_points)
    y = eval_chg_path(r1, r2 , filename, n_points)
    ax.plot(x,y)
    ax.set_xticks([0,1])
    ax.set_xticklabels(["r1","r2"])
    ax.set_xlim(-0.2,1.2)
    

if __name__ = '__main__':
	if input("Show structure? [y/n]")[0] == 'y':
		view('POSCAR')
    else:
    	pass

    atoms = read("POSCAR")
    
