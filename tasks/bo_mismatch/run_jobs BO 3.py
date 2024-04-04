import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
from utils.runners import runner
import numpy as np


params_model = {
    "group_name" : "BO 3.lammps",
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
    "record_interval" : 1e-1,
    # "algorithm" : "VERLET",
}

n=20
if __name__ == "__main__":
    for k in range(0, n+1):
        scale_max = 4
        scale = (scale_max**3 * k / n + (1-k/n) * 1**3)**(1/3)

        params_model["R"] = 1 * scale
        params_model["Rz"] = 0.25* scale
        # print("sigma_grid= ", sigma_grid)
        N = submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=20, 
            job_name="BO 3 LAMMPS",
            print_summary=False, time_factor=17, memory_factor=4, success_email=False)
        
        print((((4*np.pi/3) * params_model["R"]**2 * params_model["Rz"])/N)**(1/3))



    # submit_all_jobs(as_array=True)
