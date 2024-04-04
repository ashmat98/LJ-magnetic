#!/usr/bin/env python

import adddeps
import argparse
import os
import shutil

from simulator.hdf5IO import Client_HDF5, Simulation
from simulator.models import Client, SimulationAlchemy as Sim
from settings import HDF5_PATH, RESULT_PATH
from tqdm import tqdm

from utils.export import export_for_mathematica

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    output_path = "/data/biophys/ashmat/mathematica_exports"
    parser.add_argument("groups", type=str, nargs="+", default=None)
    parser.add_argument("--prefix", type=str, default="sim")
    
    args = parser.parse_args()

    # print(args.prefix, args.groups)
    export_for_mathematica(args.groups,output_path, args.prefix)