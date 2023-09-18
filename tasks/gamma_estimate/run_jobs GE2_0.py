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
    "group_name" : "GE 2.0",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.0,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy_for_position_init":1,
    # "energy": 1,
    "sigma_grid":0.23,
    "position_random_shift_percentage": 0.0/100,
    # "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    # "iteration_time" : 1,
    "iteration_time" : 4000,
    "dt" : 1e-3,
    "record_interval" : 1e-1,
    "algorithm" : "VERLET",
    # "before_step" : "tasks.gamma_estimate.run_jobs GE1_0.before_step"
}

if __name__ == "__main__":
    omegas = np.linspace(0,0.95,20)
    temps = np.linspace(0.1, 0.5, 20)

    i=0
    for o in omegas:
        for t in temps:
            params_init["angular_momentum"] = 343 * t * 2 * o / (1-o**2)
            params_init["energy"] = t * (3 - o**2) / (1 - o**2)
            if params_init["energy"]<1:
                continue

            submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=10, 
                job_name=f"{params_model['group_name']} {i}",
                print_only=True, time_factor=1.5, memory_factor=2, success_email=True)
            
            i+=1

    submit_all_jobs()



