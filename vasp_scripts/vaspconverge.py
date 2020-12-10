#!/usr/bin/env python
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib import font_manager as fm
import os

import matplotlib.ticker

axes_lw = 0.9

class MyLocator(matplotlib.ticker.AutoMinorLocator):
    def __init__(self, n=2):
        super().__init__(n=n)
matplotlib.ticker.AutoMinorLocator = MyLocator

def figsize_in_cm(x, y):
    return (x/2.54, y/2.54)

# My font path
font_path = "/home/hmj0327/fonts"
font_files = fm.findSystemFonts(fontpaths=font_path)
for font in font_files:
    fm.fontManager.addfont(font)

# General font settings
mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['font.size'] = 8
mpl.rcParams['mathtext.default'] = 'regular'
mpl.rcParams['text.usetex'] = False

# Color settings
mpl.rcParams['axes.prop_cycle'] = cycler(color='krbgcmy')

# Figure properties
mpl.rcParams['figure.figsize'] = figsize_in_cm(8, 6)
mpl.rcParams['figure.dpi'] = 200

# Axes properties
mpl.rcParams['axes.linewidth'] = axes_lw
mpl.rcParams['axes.labelsize'] = 9.5
mpl.rcParams['axes.titlesize'] = 9.5

# Ticks properties
mpl.rcParams["xtick.minor.visible"] =  True
mpl.rcParams["ytick.minor.visible"] =  True
mpl.rcParams["xtick.direction"] = 'in'
mpl.rcParams['xtick.major.size'] = 2.5
mpl.rcParams['xtick.major.width'] = axes_lw
mpl.rcParams['xtick.minor.size'] = 1.4
mpl.rcParams['xtick.minor.width'] = axes_lw
mpl.rcParams["ytick.direction"] = 'in'
mpl.rcParams['ytick.major.size'] = 2.5
mpl.rcParams['ytick.major.width'] = axes_lw
mpl.rcParams['ytick.minor.size'] = 1.4
mpl.rcParams['ytick.minor.width'] = axes_lw

# Legend properties
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.edgecolor'] = 'k'
mpl.rcParams['legend.fancybox'] = False
mpl.rcParams['legend.fontsize'] = 8




plt.rc('font',family='Lato', weight='semibold')
plt.rc('axes',labelweight='semibold')

lw = 0.25
ms = 2.4

os.system("vef.py")

fe = np.loadtxt("fe.dat", skiprows=1).T

fig, ax = plt.subplots(figsize=figsize_in_cm(10,7))
ax2 = ax.twinx()
ax.set_xlabel("Ionic step")
ax.set_ylabel("Force (eV/$\AA$)",color='blue')
ax.set_yscale('log')
ax2.set_ylabel("Total energy (eV)", color='red')
ax.plot(fe[0],fe[1],'bo-', lw=lw,ms=ms,markeredgewidth=0.25,markerfacecolor='none',label='force')
ax2.plot(fe[0],fe[2],'rs--', lw=lw,ms=ms-0.25,markeredgewidth=0.25,markerfacecolor='none',label='energy')

ax.tick_params(axis='y', which='both', colors='b')
ax2.tick_params(axis='y',which='both', colors='r')
plt.tight_layout()
plt.savefig('vasp_convergence.png', dpi=600)
plt.show()

