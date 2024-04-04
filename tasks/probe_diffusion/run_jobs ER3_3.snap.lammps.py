import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np

# 11870576
# 11871855

params_model = {
    "group_name" : "ER 3.303.snap.lammps",
    "cls":"SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.0,
    "sigma":0.05,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":1,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.7,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 10000,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    "particle_properties":True,
    "total_properties": True
}

scale = 5
params_model["R"] *= scale
params_model["Rz"] *= scale


# time_estimate = int(params_simulation["iteration_time"] / params_simulation["dt"] * 0.016)
if __name__ == "__main__":
    submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                    copies=10, 
                                    time_estimate=2 * 86400,
                                    time_factor=1, memory_factor=2,
                                    job_name="ER-snap",success_email=True)
        
    submit_all_jobs()
