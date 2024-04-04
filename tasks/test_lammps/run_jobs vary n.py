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

eccentricity_1 = 0.4

params_model = {
    "group_name" : "time estimate; N vary; partition medium; fastrelaxation",
    "cls": "SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    # "eccentricity": 0.085,
    "sigma":0.05,
    "epsilon":0.1,
}


params_init = {
    "energy": 1,
    "sigma_grid":1,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "warmup":0,
    "iteration_time" : 5000,
    "dt" : 1e-3,
    "record_interval" : 5e-1,
    # "output_particles" : 5,
    "particle_properties":True,
    "total_properties": True
}



if __name__=="__main__":
    for scale in np.logspace(0,1,12):
        params_model["R"] = 1.0 * scale
        params_model["Rz"] = 0.25 * scale
        params_model["eccentricity"] = eccentricity_1 / np.sqrt(scale)

        submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=30, 
                    job_name=f"TE long partition",
                    time_estimate=86400*2-4000,
                    print_summary=True, time_factor=1, memory_factor=4, success_email=False)
        
        

    submit_all_jobs(as_array=True)
