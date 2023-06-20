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

import os
import json


from utils.runners import runner

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=os.getenv("PARAMS_MODEL"), required=False)
    parser.add_argument("--init", type=str, default=os.getenv("PARAMS_INIT"), required=False)
    parser.add_argument("--simulation", type=str, default=os.getenv("PARAMS_SIMULATION"), required=False)
    
    args = parser.parse_args()
    print([args.model, args.init, args.simulation])
    # if args.model is None:
    #     args.model = os.getenv("PARAMS_MODEL")
    # if args.init is None:
    #     args.init = os.getenv("PARAMS_INIT")
    # if args.simulation is None:
    #     args.simulation = os.getenv("PARAMS_SIMULATION")
    
    try:
        params_model=json.loads(args.model)
        params_init=json.loads(args.init)
        params_simulation=json.loads(args.simulation)
    except Exception as e:
        print("Error in parsing arguments!")
        raise e
    
    try:
        output_path = runner(params_model, params_init, params_simulation)
        print(output_path)
    except Exception as e:
        print("Error in running simulation!")
        raise e
    