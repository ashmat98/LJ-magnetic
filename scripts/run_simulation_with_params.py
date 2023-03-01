#!/usr/bin/env python

import adddeps
import argparse

import numpy as np
from simulator.magnetic import SimulatorMagnetic

import os, time
import json

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
    