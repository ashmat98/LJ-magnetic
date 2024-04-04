#!/usr/bin/env python

from collections import Counter
import adddeps
import argparse
import os
import shutil

from simulator.hdf5IO import Client_HDF5, Simulation
from simulator.models import Client, SimulationAlchemy as Sim
from settings import HDF5_PATH, RESULT_PATH
from tqdm import tqdm
import h5py


def clean_fields(hash):
    path = os.path.join(HDF5_PATH, hash+".hdf5")
    with h5py.File(path, "a") as ds:
        for key in ds.keys():
            if key not in ["total", "vs", "rs", "time"]:
                del ds[key]
                # print("del", key)
    os.system(f"h5repack \"{path}\" \"{path}.hdf5\"")
    os.remove(path)
    os.rename(path+".hdf5", path)


if __name__=="__main__":
    group_names = ["ER 3.303.35.lammps",
        "ER 3.303.55.lammps",
        "ER 3.303.45.lammps",
        "ER 3.303.6.lammps",
        "ER 3.303.15.lammps",
        "ER 3.303.25.lammps"]

    client = Client()
    with client.Session() as sess:
        hashs = sess.query(Sim.hash).where(Sim.group_name.in_(group_names)).all()

    print(len(hashs))
    for hash, in tqdm(hashs[::]):
        try:
            clean_fields(hash)
        except Exception as e:
            print("Exception with", hash)
            print("\t", str(e))
        # break