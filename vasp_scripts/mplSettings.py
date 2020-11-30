#!/usr/bin/env python
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal._savitzky_golay import savgol_filter as savgol
from cycler import cycler
import matplotlib.ticker

import matplotlib.font_manager as fm


class MyLocator(matplotlib.ticker.AutoMinorLocator):
    def __init__(self, n=2):
        super().__init__(n=n)


matplotlib.ticker.AutoMinorLocator = MyLocator


def figsize_in_cm(x, y):
    return (x / 2.54, y / 2.54)


# General font settings
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
mpl.rcParams["legend.fontsize"] = 6

# plot setting
mpl.rcParams["lines.linewidth"] = 0.8
mpl.rcParams["lines.markersize"] = 3
