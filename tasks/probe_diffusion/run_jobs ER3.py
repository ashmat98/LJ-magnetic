import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np

# slower relaxation then ER 2

params_model = {
    "group_name" : "ER 3",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.15,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":0.25,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 40000,
    "dt" : 1e-3,
    "record_interval" : 1e-1,
    "algorithm" : "VERLET",
}

submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                 copies=90, 
                                 job_name="extra_long ER 3")
    
submit_all_jobs()
    