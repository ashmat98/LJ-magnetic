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
    "group_name" : "Ensemble 4.1.lammps",
    "cls": "SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.00,
    "sigma":0.05,
    "epsilon":0.1
}
params_init = {
    "energy": 1,
    "sigma_grid":0.1,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.6,
    # "angular_momentum" : 60,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 15000,
    "dt" : 1e-4,
    "record_interval" : 1e-1,
    "particle_properties":True,
    "total_properties": True
}

scale = 0.5
params_model["R"] *= scale
params_model["Rz"] *= scale

if __name__=="__main__":
    submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=20, 
                job_name=f"{params_model['group_name']}", time_estimate=86400*2-25*60,
                print_summary=True, time_factor=1., memory_factor=4, success_email=False)

    submit_all_jobs(as_array=True)
