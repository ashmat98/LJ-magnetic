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
from tqdm.notebook import tqdm as tqdm_notebook

from utils.utils import beep

def multirunner(params, callback=None, processes=-1, pool=None):
    if processes == -1:
        processes = cpu_count()

    if pool is None:
        pool = Pool(processes, maxtasksperchild=1)

    new_params = []
    for i, (params_model, params_init, params_simulation) in enumerate(params):
        params_model = params_model.copy()
        params_model["verbose"] = (i==0)
        new_params.append((params_model, params_init, params_simulation, callback))
        
    res_generator = pool.imap(_runner, new_params[1:])
    res = [_runner(new_params[0])]
    res += list(tqdm_notebook(res_generator, total=len(new_params)-1))

    return res

def _runner(args):
    return runner(*args)   

def runner(params_model, params_init, params_simulation, callback=None):
    params_model["name"] = params_model.get("name", os.getenv("HOSTNAME"))

    sim = SimulatorMagnetic(**params_model)

    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)

    if callback is not None:
        return callback(sim)
    
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
    