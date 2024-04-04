# -*- coding: utf-8 -*-

import h5py
import pandas as pd
import numpy as np
import sys
import os

def f(hdf5_path):
    data = {}
    
    history = dict()
    with h5py.File(hdf5_path, 'r') as f:
        for key in f:
            history[key] = np.array(f[key])
        particles = f.attrs.get("particles")
    
    
    ts = history["time"].round(5)
    rs = history["rs"].transpose(1,0,2)
    vs = history["vs"].transpose(1,0,2)
    data["time"] = ts
    data["N"] = np.ones_like(ts) * particles
    data["Iz"] = np.sum(rs[0]**2+rs[1]**2, axis=-1)
    
    data["xx"] = np.mean(rs[0]**2,axis=-1)
    data["yy"] = np.mean(rs[1]**2,axis=-1)
    data["zz"] = np.mean(rs[2]**2,axis=-1)
    data["xy"] = np.mean(rs[0]*rs[1],axis=-1)
    
    
    omega_MLE = np.mean(rs[0]* vs[1]-rs[1]* vs[0], axis=1) / np.mean(rs[0]**2+rs[1]**2, axis=-1)

    beta_MLE  = (1/3 * np.mean( (vs[0]+omega_MLE[:,None] * rs[1])**2 + (vs[1]-omega_MLE[:,None] * rs[0])**2 + (vs[2])**2,axis=-1))**-1

    data["omega_MLE"] = omega_MLE
    data["beta_MLE"] = beta_MLE

    data["total_L"] = history["L"][:,2].sum(axis=-1)
    data["total_E"] = np.sum(0.5 * history["IE"] + history["PE"] + history["KE"], axis=-1)
    data["total_KE"] = np.sum(history["KE"], axis=-1)
    data["total_IE"] = np.sum(0.5 * history["IE"], axis=-1)
    
    if "collisions" in history:
        for i, c in enumerate(history["collisions"].T):
            data[f"collisions-{i+1}"] = c
    
    df = pd.DataFrame(data).set_index("time")
    return df

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    df = f(input_file)
    df.to_hdf(output_file, key='df', mode='w')
    