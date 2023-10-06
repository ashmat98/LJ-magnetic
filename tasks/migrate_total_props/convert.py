# -*- coding: utf-8 -*-
import os
if os.path.exists("adddeps.py"):
    import adddeps
import h5py
import pandas as pd
import numpy as np
import sys
from utils.convert import convert_particle_prop_to_total_prop

def f(hdf5_path):
    # with h5py.File(hdf5_path, "r+") as f:
    #     print(f.keys())
    #     f.pop("total/yy")
    #     f["total/yy"] = np.array([1,2,3])
    # return
    new_history = convert_particle_prop_to_total_prop(hdf5_path)
    print(new_history.keys())
    with h5py.File(hdf5_path, "r+") as f:
        for key, value in new_history.items():
            # print(key)
            f.pop(key)
            f[key] = value

if __name__ == "__main__":
    input_file = sys.argv[1]

    f(input_file)
    