import datetime
import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np

# 11870576
# 11871855

params_model = {
    "group_name" : "ER 3.404.weak.lammps",
    "cls":"SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "sigma":0.05,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":1,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "warmup":5000,
    "iteration_time" : 700000,
    "dt" : 1e-3,
    "record_interval" : 1,
    "output_particles" : 50,
    "particle_properties":True,
    "total_properties": True
}

scale = 3.65
eccentricity_1 = 0.085

params_model["R"] *= scale
params_model["Rz"] *= scale
# params_model["eccentricity"] = eccentricity_1 / np.sqrt(scale)
params_model["eccentricity"] = 0.0285


# time_estimate = int(params_simulation["iteration_time"] / params_simulation["dt"] * 0.016)
if __name__ == "__main__":
    submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                    copies=600, 
                                    time_estimate=86400*2-25*60-1,
                                    time_factor=1, memory_factor=4,
                                    job_name="ER-200-3-weak",success_email=True)
        
    submit_all_jobs()
