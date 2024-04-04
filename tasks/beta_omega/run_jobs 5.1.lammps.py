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
from utils.submit_job import submit_all_jobs, submit_with_estimates_and_params
from utils.utils import beep
from tqdm.notebook import tqdm 

import sys, os, time
params_model = {
    "group_name" : "Ensemble 5.1.lammps",
    "cls": "SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.00,
    "sigma":0.05,
    "epsilon":0.1,
}
params_init = {
#     "energy": 10,
#     "sigma_grid":2,
    "position_random_shift_percentage": 50.0/100,
#     "angular_momentum_factor" : 0.99,
#     "angular_momentum" : 60,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 2000,
    "dt" : 1e-4,
    "record_interval" : 1e-1,
    # "algorithm" : "VERLET",
#     "before_step" : before_step
}
# factor 20 to time

sz = 40
grid = [x.flatten() for x in np.meshgrid(
    np.logspace(0.1, 10, sz),
    np.linspace(0,0.97,sz), 
    np.linspace(0.1, 2,sz))]

grid_filtered = []
for energy, angular_momentum_factor, sigma_grid in zip(*grid):
    N_pred = ((energy / sigma_grid**2)**(1.5)*4.2)
    if N_pred < 10 or N_pred > 205:
        continue
    grid_filtered.append([energy, angular_momentum_factor, sigma_grid, N_pred])


grid_filtered = np.array(grid_filtered)

rng = np.random.default_rng(2023)
perm = rng.permutation(len(grid_filtered))
grid = grid_filtered[perm]

print("Number of simulations:",len(grid))
print("Maximum lasting index:",grid[:,3].argmax())

if __name__=="__main__":
    for i in range(10,len(grid)):
        energy, angular_momentum_factor, sigma_grid, _ = grid[i]
        params_init["energy"] = energy
        params_init["angular_momentum_factor"] = angular_momentum_factor
        params_init["sigma_grid"] = sigma_grid
        submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=1, 
                    job_name=f"{params_model['group_name']}",
                    print_summary=True, time_factor=1.5, memory_factor=1.5, success_email=False)

    submit_all_jobs(as_array=True)
