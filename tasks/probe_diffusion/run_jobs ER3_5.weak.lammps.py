import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np

# 11870576
# 11871855

params_model = {
    "group_name" : "ER 3.500.weak.lammps",
    "cls":"SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.038,
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
    "iteration_time" : 200000,
    "dt" : 1e-3,
    "record_interval" : 5e-1,
    "output_particles" : 150,
    "particle_properties":True,
    "total_properties": True
}

scale = 5
params_model["R"] *= scale
params_model["Rz"] *= scale

epss = [{"esp":0.00006,"%":6},
 {"esp":0.000095,"%":15},
 {"esp":0.00013,"%":25},
#  {"esp":0.00015,"%":30},
 {"esp":0.000166,"%":35},
 {"esp":0.0002,"%":45},
 {"esp":0.000243,"%":55},
]
 


# time_estimate = int(params_simulation["iteration_time"] / params_simulation["dt"] * 0.016)
if __name__ == "__main__":
    for line in epss:
        params_model["eccentricity"] = 2 * np.sqrt(line["esp"])
        params_model["group_name"] = "ER 3.303.{}.lammps".format(line["%"])
        
        print(params_model["group_name"] )
        submit_with_estimates_and_params(params_model, params_init, params_simulation,
                                        copies=1000, 
                                        time_estimate=86400*2-25*60-1, time_factor=1,
                                        memory_factor=4,
                                        job_name="ER-5",success_email=True)
            
    submit_all_jobs()
