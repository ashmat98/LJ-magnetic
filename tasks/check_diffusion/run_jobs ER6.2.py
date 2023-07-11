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
    "group_name" : "ER 6.2",
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
    "iteration_time" : 1450,
    "dt" : 1e-3,
    "record_interval" : 2e-1,
    "algorithm" : "VERLET",
    "before_step" : "tasks.check_diffusion.run_jobs ER6.before_step"
}


n=4
sigma_min = 0.16
sigma_max = 0.23

if __name__ == "__main__":
    for k in range(n+1):
        # if True or k != 17:
        #     continue
        sigma_grid = (sigma_min**-3 * k / n + (1-k/n) * sigma_max**-3)**(-1/3)
        p=0.3
        iteration_time = int( (1450**-p * k / n + (1-k/n) * 10000**-p)**(-1/p) )
        print(iteration_time)
        params_init["sigma_grid"] = sigma_grid
        params_simulation["iteration_time"] = iteration_time
        
        print("sigma_grid= ", sigma_grid)
        submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=150, 
            job_name=f"diffusion coefficient {params_model['group_name']} {k}",
            print_only=True, time_factor=1.3, memory_factor=2, success_email=True)

    submit_all_jobs()



