#%%
import time
time_last = time_start = time.time()

import numpy as np
import h5py
import os
import sys
import json 


def print_seconds(prefix):
    global time_last
    t = time.time()
    print(prefix + f": {int(t-time_last)} {int(t-time_start)}")
    time_last = t

print_seconds("imports")



path = sys.argv[1]
# path = "/home/ashmat/Desktop/187cbf719c4e77ed.hdf5"
print("Path:",path)

# exit(0)


def angular_momentum(r, v) -> np.ndarray:
    return np.cross(r.T, v.T).T
def f(path):
    ds = h5py.File(path)
    

    start = np.searchsorted(ds["time"][:], 40)

    TE = (ds["KE"][:] + ds["PE"][:] + 0.5*ds["IE"][:]).sum(axis=1)    
    KE = ds["KE"][start:].mean()
    PE = ds["PE"][start:].mean()
    IE = ds["IE"][start:].mean()


    rs, vs = ds["rs"][:], ds["vs"][:]
    
    N = rs.shape[2]
    L = angular_momentum(rs[0], vs[0])[2].sum()
    
    rs = rs[start:].transpose(0,2,1).reshape(-1,3).T
    vs = vs[start:].transpose(0,2,1).reshape(-1,3).T
    
    omega_MLE = np.mean(rs[0]*vs[1]-rs[1]*vs[0])/np.mean(rs[0]**2+rs[1]**2)
    beta_MLE  = (1/3 * np.mean( (vs[0]+omega_MLE * rs[1])**2 + (vs[1]-omega_MLE * rs[0])**2 + (vs[2])**2) )**-1
    
    return {"omega_MLE" : omega_MLE,
            "beta_MLE" : beta_MLE,
            "N" : ds.attrs["particles"],
            "L" : L,
            "L_init": ds.attrs["L_init"],
            "E_init": ds.attrs["E_init"],
            "E" : TE[0],
            "E_end" : TE[-1],
            "alpha" : ds.attrs["a"]**-1,
            "xx": np.mean(rs[0]**2),
            "yy": np.mean(rs[1]**2),
            "zz": np.mean(rs[2]**2),
            "KE": KE, "PE":PE,"IE":IE,
           }

datum = f(path)

print_seconds("precalculations")
#%%

with open("out.json", "w") as f:
    json.dump({k:float(v) for k,v in datum.items()}, f)

# %%
