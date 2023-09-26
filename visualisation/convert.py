#!/usr/bin/env python3
import adddeps

import os
import argparse
import numpy as np
import MDAnalysis as mda
import h5py
from tqdm import tqdm
from settings import HDF5_PATH

def R(phi):
    return np.array([
        [np.cos(phi), np.sin(phi), 0],
        [-np.sin(phi), np.cos(phi), 0],
        [0,0,1]
    ])

def convert(input_path, output_path):
    with h5py.File(input_path) as ds:
        rs = ds["rs"][:]
        vs = ds["vs"][:]
        dt = ds["time"][1] - ds["time"][0]

    print("record_interval=",dt)
    
    L = rs[:,0] * vs[:,1] - rs[:,1] * vs[:,0]


    Omega = L.sum(axis=1)/(rs[:,:2]**2).sum(axis=(1,2))
    N = 1000
    Omega = np.convolve(Omega, np.ones(N)/N, mode='same')
    phis = np.cumsum(Omega * dt)
    
    print(Omega.shape, rs.shape)


    n_frames, _, n_atoms = rs.shape

    universe = mda.Universe.empty(n_atoms=n_atoms, trajectory=True)
    dcd_writer = mda.Writer(output_path, n_atoms=n_atoms)
    
    for frame_number, (positions, phi) in tqdm(enumerate(zip(rs, phis)), total=n_frames):
        universe.atoms.positions = positions.T.dot(R(-phi))
    
        dcd_writer.write(universe.atoms)

    dcd_writer.close()


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", type=str)
    parser.add_argument("output", default=None)
    args = parser.parse_args()
    
    if args.output is None:
        args.output = args.hash 

    input_path = os.path.join(HDF5_PATH, args.hash + ".hdf5")

    visualisation_dir, _ = os.path.split(os.path.realpath(__file__))

    output_path = os.path.join(visualisation_dir,"outputs", args.output + ".dcd")
    
    convert(input_path, output_path)