#!/usr/bin/env python

"""
Usefull code:

from multiprocessing import Pool, cpu_count
from tqdm import tqdm 
from utils.utils import beep

if "pool" in dir():
    pool.close()
    print("closed")
pool = Pool(cpu_count(), maxtasksperchild=1); pool

n_ = cpu_count()
res = list(tqdm(pool.imap(f, range(n_)), total=n_))
beep()

"""


import adddeps
import argparse

import numpy as np
from simulator.magnetic import SimulatorMagnetic

import os, time
import json

from multiprocessing import Pool, cpu_count
from tqdm import tqdm 
from utils.utils import beep

def multirunner(params, processes=-1):
    pool = None #TODO: fix this
    for (params_model, params_init, params_simulation) in params:
        pass


def runner(params_model, params_init, params_simulation):
    params_model["name"] = params_model.get("name", os.getenv("HOSTNAME"))
    sim = SimulatorMagnetic(
        name=os.getenv("HOSTNAME"),
        **params_model)
    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)
    return sim.push_hdf5()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--init", type=str, required=True)
    parser.add_argument("--simulation", type=str, required=True)
    
    args = parser.parse_args()
    try:
        params_model=json.loads(args.model)
        params_init=json.loads(args.init)
        params_simulation=json.loads(args.simulation)
    except Exception as e:
        print("Error in parsing arguments!")
        raise e
    
    try:
        runner(params_model, params_init, params_simulation)
    except Exception as e:
        print("Error in running simulation!")
        raise e
    