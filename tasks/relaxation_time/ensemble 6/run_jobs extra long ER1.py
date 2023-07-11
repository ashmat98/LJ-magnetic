import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np


params_model = {
    "group_name" : "ER 1",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.0,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":0.36,
    "position_random_shift_percentage": 0.0/100,
    # "angular_momentum_factor" : 0.5,
    "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 20000,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    "algorithm" : "VERLET",
}

submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                 copies=10, 
                                 job_name="extra_long")
    
submit_all_jobs()
    