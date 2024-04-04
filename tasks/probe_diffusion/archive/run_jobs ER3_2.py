import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np

# slower relaxation then ER 2

def before_step(obj, r, v, t):
    if not hasattr(obj, "abc_dummy"):
        obj.abc_dummy = obj.abc.copy()
        obj.abc[1] = obj.abc[0]
        obj.init_potential_params()
        
    if t > 5000:
        obj.abc = obj.abc_dummy
        obj.init_potential_params()
        obj.last_a = None


params_model = {
    "group_name" : "ER 3.2",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.15,
    "sigma":0.15,
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
    "iteration_time" : 45000,
    "dt" : 1e-3,
    "record_interval" : 1e-1,
    "algorithm" : "VERLET",
    "before_step" : "tasks.probe_diffusion.run_jobs ER3_2.before_step"
}

time_estimate = int(params_simulation["iteration_time"] / params_simulation["dt"] * 0.016)
if __name__ == "__main__":
    submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                    copies=200, time_factor=1.3, time_estimate=time_estimate,
                                    job_name="ER 3.2")
        
    submit_all_jobs()
