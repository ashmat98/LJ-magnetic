import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np


params_model = {
    "group_name" : "BO 1.1.lammps",
    "cls": "SimulatorLennardLammps",
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
    "angular_momentum_factor" : 0.0,
#     "angular_momentum" : 44,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 1000,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    # "algorithm" : "VERLET",
}

n=10
sigma_min = 0.15
sigma_max = 0.50

if __name__ == "__main__":
    for k in range(n+1):
        sigma_grid = (sigma_min**-3 * k / n + (1-k/n) * sigma_max**-3)**(-1/3)
        params_init["sigma_grid"] = sigma_grid
        print("sigma_grid= ", sigma_grid)
        submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=40, 
            job_name="BO LAMMPS",
            print_summary=True, time_factor=0.1, memory_factor=4, success_email=False)
        
    submit_all_jobs(as_array=True)
