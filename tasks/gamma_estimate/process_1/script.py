#%%
import time
time_last = time_start = time.time()

import numpy as np
import h5py
import os
import sys

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


ds = h5py.File(path, "r")
rs = ds["rs"][:]
vs = ds["vs"][:]
ts = ds["time"]
print_seconds("load rsvs")
#%%
_i_start = len(rs)*500//3000
rs = rs[_i_start:]
vs = vs[_i_start:]
ts = ts[_i_start:]-ts[_i_start]
dt = ts[1]-ts[0]
L = rs[:,0] * vs[:,1] - rs[:,1] * vs[:,0]

Omega = L.sum(axis=1)/(rs[:,:2]**2).sum(axis=(1,2))
O = np.mean(Omega)
T = np.mean(((vs[:,0] + O*rs[:,1])**2+(vs[:,1] - O*rs[:,0])**2 + (vs[:,2])**2)/3,axis=1)
T = T.mean()

vc = vs[:,0] + 1j * vs[:,1]
vc_relative = vc * np.exp(-1j*O*ts)[:,None]
wc = vc + O*(rs[:,1]-1j * rs[:,0])
wc_relative = wc * np.exp(-1j*O*ts)[:,None]

def AC(x):
    n = len(x)
    ac = np.correlate(x, x, "full")
    w = np.arange(n, 0, -1)
    ac = ac[n-1:] / w
    return ac

print_seconds("precalculations")
#%%

W = 10000
particles = vc.shape[1]
# particles = 1

ac = {}
for name,val in {"vc":vc,"vc_relative":vc_relative, "wc":wc,"wc_relative":wc_relative}.items():
    ac[name] = [AC(val[:,k])[:W] for k in range(particles)]

# ac_relative = np.mean([AC(vc_relative[:,k])[:W] for k in range(particles)], axis=0)
# ac = np.mean([AC(vc[:,k])[:W] for k in range(particles)], axis=0)

print_seconds("autocorrelation")


# %%
with h5py.File("out.hdf5", "w") as ds:
    for k, val in ac.items():
        ds["ac_"+k] = val
    ds.attrs["O"] = O
    ds.attrs["T"] = T
