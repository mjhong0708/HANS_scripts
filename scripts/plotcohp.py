#!/usr/bin/env python
from pymatgen.io.lobster.outputs import Cohpcar
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from mplSettings import *
from matplotlib import font_manager as fm, rcParams
import os
import pandas as pd 


fpath = os.path.join(rcParams["datapath"], "/home/hmj0327/anaconda3/lib/python3.8/site-packages/matplotlib/mpl-data/fonts/ttf/Arial.ttf")
prop = fm.FontProperties(fname=fpath)

print("Reading COHPCAR.lobster...")
cohpcar = Cohpcar('COHPCAR.lobster')
cohpdata = cohpcar.cohp_data
interactions = list(cohpdata.keys())

print("Sucessfully read")
print("Available interactions: ")
print(list(cohpdata.keys()))
selected_interactions = []
while True:
    interaction = input("Add interaction (enter done to exit): ")
    if interaction == "done":
        break
    if interaction not in interactions:
        print("Wrong interaction.")
        continue
    else:
        selected_interactions.append(interaction)
        print(f"Interaction '{interaction}' added")
print("Interactions saved.")


def plot_cohp(cohpcar, interaction):
    E = cohpcar.energies
    cohpdata = cohpcar.cohp_data
    cohp = sum(cohpdata[interaction]["COHP"].values())
    plt.plot(-cohp, E, label=f"interaction {i}")
    plt.axvline(x=0, color="k", linestyle="-")
    plt.axhline(y=0, color="k", linestyle="--")




plot_or_save = input('Plot or save?[p/s]')

if plot_or_save == 'p':
    xmin = float(input("Enter xmin: "))
    xmax = float(input("Enter xmax: "))
    ymin = float(input("Enter ymin: "))
    ymax = float(input("Enter ymax: "))
    plt.figure(figsize=figsize_in_cm(7, 9))
    plt.xlabel("-pCOHP",fontproperties = prop)
    plt.ylabel("E (eV)",fontproperties = prop)
    for i in selected_interactions:
        plot_cohp(cohpcar, i)
    plt.xlim((xmin, xmax))
    plt.ylim((ymin, ymax))
    plt.legend()
    plt.tight_layout()
    plt.savefig('cohp_plot.png', transparent=True, dpi = 600)
    plt.show()

elif plot_or_save == 's':
    save_data = pd.DataFrame()
    E = cohpcar.energies
    save_data['E'] = E
    cohpdata = cohpcar.cohp_data
    for interaction in selected_interactions:
        cohp = sum(cohpdata[interaction]["COHP"].values())
        save_data[cohpdata[interaction]['sites']] = cohp
    save_data.to_csv("cohp_data.csv", index=False)



