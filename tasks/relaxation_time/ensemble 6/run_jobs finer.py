import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np


params_model = {
    "group_name" : "Ensemble 9.1",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.0,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":0.4,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.95,
#     "angular_momentum" : 44,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 300,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    "algorithm" : "VERLET",
}

n=7
sigma_min = 0.27
sigma_max = 0.45

for k in range(n+1):
    sigma_grid = (sigma_min**-3 * k / n + (1-k/n) * sigma_max**-3)**(-1/3)
    params_init["sigma_grid"] = sigma_grid
    print("sigma_grid= ", sigma_grid)
    submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=20, 
        job_name="relaxation_finder",
        print_only=True)
    
# submit_all_jobs()
    




# runner(params_model, params_init, params_simulation)
