#!/usr/bin/env python
import pandas as pd
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", -1)
with open("ACF.dat", "r") as acf:
    lines = np.array([l.split() for l in acf.readlines()[2:-4]])
    lines = lines.astype("float").T


# %%
print(pd.DataFrame({"Atom": lines[0].astype("int"), "Charge": lines[4]}))
