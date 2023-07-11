import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np


params_model = {
    "group_name" : "ER 5",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.2,
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
    "iteration_time" : 10000,
    "dt" : 1e-3,
    "record_interval" : 2e-1,
    "algorithm" : "VERLET",
}

n=20
sigma_min = 0.23
sigma_max = 0.50

for k in range(n+1):
    if True and k != 17:
        continue
    sigma_grid = (sigma_min**-3 * k / n + (1-k/n) * sigma_max**-3)**(-1/3)
    params_init["sigma_grid"] = sigma_grid
    print("sigma_grid= ", sigma_grid)
    submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=100, 
        job_name=f"diffusion coefficient {params_model['group_name']} {k}",
        print_only=True, time_factor=1.4)
    

submit_all_jobs()
