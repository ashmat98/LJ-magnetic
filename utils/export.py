
import os
import numpy as np

import pandas as pd
from tqdm import tqdm
from simulator.models import Client

from utils.utils import smoothen, concat, df_round_time

import h5py


def export_for_mathematica(group_names, output_path, file_prefix, shift=5000):

    client = Client()
    items = client.get_simulation_groups(group_names)
    [item.load_df() for item in tqdm(items)]
    items = [item for item in items if item.df is not None]
    for item in items:
        item.df = df_round_time(item.df)

    item = items[0]

    file_name = file_prefix + "-{}-{:0.4f}-{}-({}).h5".format(
        item.particles,item.eccentricity,int(item.df.index[-1]),
        len(items)
    )

    output_path = os.path.join(output_path, file_name)
    print("Output path:", output_path)

    dfs = [item.df.set_index(item.df.index-shift) for item in items]


    N = item.particles
    # N = int(df["N"].iloc[0])

    df_L = concat([df.L for df in dfs])
    df_T = concat([1/df.beta_MLE for df in dfs])
    df_omega = concat([df.omega_MLE for df in dfs])
    df_xy = smoothen(concat([df.xy for df in dfs]),-1)

    df_zz = concat([df.zz for df in dfs])

    df_IE = smoothen(concat([df["IE"] for df in dfs]),-1)
                    
    df_KPE = concat([df["E"]-df["IE"] for df in dfs])

    df_KE = concat([df["KE"] for df in dfs])




    df_exported = pd.DataFrame({
        "O":df_omega.mean(axis=1).loc[0:],
        "L":df_L.mean(axis=1).loc[0:],
        "xy":df_xy.mean(axis=1).loc[0:],
        "T":df_T.mean(axis=1).loc[0:],
        "zz":df_zz.mean(axis=1).loc[0:],
        "E":df_KPE.mean(axis=1).loc[0:],
        "K":df_KE.mean(axis=1).loc[0:],

        "Lstd":df_L.std(axis=1).loc[0:],
        "Tstd":df_T.std(axis=1).loc[0:],

    }
    ).to_hdf(output_path, key="/df")

    with h5py.File(output_path, "r+") as f:
        f.attrs["particles"] = item.particles
        f.attrs["ax"], f.attrs["ay"], f.attrs["az"] = 1/item.a, 1/item.b, 1/item.c
        f.attrs["a"] = (f.attrs["ax"] + f.attrs["ay"])/2
        f.attrs["eps"] = (f.attrs["ay"] - f.attrs["ax"])/2/f.attrs["a"]

        # print(f.attrs.keys())
