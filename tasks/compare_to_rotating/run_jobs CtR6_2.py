import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
import numpy as np


# allow initial relaxation for 200 time unit

def before_step(obj, r, v, t):
    if not hasattr(obj, "abc_dummy"):
        obj.abc_dummy = obj.abc.copy()
        obj.abc[1] = obj.abc[0]
        obj.init_potential_params()
        
    if t > 200:
        obj.abc = obj.abc_dummy
        obj.init_potential_params()
        obj.last_a = None

params_model = {
    "class": "SimulatorRotating",
    "group_name" : "CtR 6.2",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.2,
    "sigma":0.1,
    "epsilon":0.1,
    "phi":0,
    "omega":0.847,
}
params_init = {
    "energy": 1,
    "sigma_grid":0.23,
    "position_random_shift_percentage": 0.0/100,
    # "angular_momentum_factor" : 0.95,
    "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    # "iteration_time" : 1,
    "iteration_time" : 10000,
    "dt" : 1e-3,
    "record_interval" : 2e-1,
    "algorithm" : "VERLET",
    "before_step" : "tasks.compare_to_rotating.run_jobs CtR6_2.before_step"
}



if __name__ == "__main__":
    submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=250, 
        job_name=f"{params_model['group_name']}",
        print_only=True, time_factor=2, memory_factor=2, success_email=True)

    submit_all_jobs()



