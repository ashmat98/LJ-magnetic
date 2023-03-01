import adddeps 
import argparse

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import importlib
from simulator.ideal import SimulatorIdeal
from simulator.lennard import SimulatorLennard
from simulator.magnetic import SimulatorMagnetic

import multiprocessing
from multiprocessing import Pool, cpu_count
from relaxation.estimators import RelaxationFinder
# import logging.config
# import logging
from utils.logs import get_logger
from utils.utils import beep, iteration_time_estimate, memory_estimate
from tqdm.notebook import tqdm 

import sys, os, time

params_model = {
    "group_name" : "Ensemble 4",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.00,
    "sigma":0.05,
    "epsilon":0.1,
    "get_logger" : get_logger
}
params_init = {
    "energy": 1,
    "sigma_grid":0.35,
    "position_random_shift_percentage": 50.0/100,
    # "angular_momentum_factor" : 0.6,
    "angular_momentum" : 60,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 1000,
    "dt" : 1e-4,
    "record_interval" : 1e-1,
    "algorithm" : "VERLET"
}



sim = SimulatorMagnetic(**params_model)
sim.init_positions_closepack(**params_init)
sim.init_velocities(**params_init)

print("number of particles: ", sim.particle_number())
print("estimated time: ", 
    (iteration_time_estimate(sim.particle_number())
    *params_simulation["iteration_time"]/params_simulation["dt"]))
print("estimated memory: ", 
    int(memory_estimate(sim.particle_number())
    *params_simulation["iteration_time"]/params_simulation["record_interval"]/1024**2), "MB")


def f(i):
    sim = SimulatorMagnetic(
        name=os.getenv("HOSTNAME"),
        **params_model)
    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)
    return sim.push_hdf5()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", type=int, default=None)
    args = parser.parse_args()

    if args.i is not None:
        f(args.i)

    