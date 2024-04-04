import adddeps 

import numpy as np

from simulator import SimulatorLennardLammps
from utils.submit_job import submit_all_jobs, submit_with_estimates_and_params
from utils.utils import beep
from tqdm import tqdm 

import sys, os, time
params_model = {
    "group_name" : "Ensemble 5.5.lammps",
    "cls": "SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.00,
    "sigma":0.05,
    "epsilon":0.1,
}
params_init = {
    "energy": 2,
    "sigma_grid":1,
    "planar": False,
    "zero_momentum": False,
    "position_random_shift_percentage":0
}
params_simulation = {
    "warmup":5000,
    "iteration_time" : 14000,
    "dt" : 1e-4,
    "record_interval" : 1e-1,
    "particle_properties":False,
    "total_properties": True
}
# factor 20 to time
scale = 5
params_model["R"] = scale
params_model["Rz"] = 0.25*scale

sim = SimulatorLennardLammps(**params_model)
sim.init_positions_closepack(**params_init)
const = scale * sim.particle_number()**(-1/3) * params_init["energy"]**0.5
print(const)

# exit(0)

sz = 20

grid_filtered = []
for E in np.logspace(-1, np.log10(20), sz):
    for N in np.linspace(10,523, sz):
        scale = const * N**(1/3) / E**0.5
        grid_filtered.append((E, scale))
        

rng = np.random.default_rng(2023)

print("Number of simulations:",len(grid_filtered) * sz)
# print("Maximum lasting index:",grid[:,3].argmax())

if __name__=="__main__":
    for E, scale in tqdm(grid_filtered):
        for _ in range(sz):
            params_init["energy"] = E
            params_init["angular_momentum_factor"] = np.random.rand() * 0.97
            params_model["R"] = scale
            params_model["Rz"] = 0.25 * scale
            submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=1, 
                        job_name=f"{params_model['group_name']}", time_estimate=86400*2-25*60-1,
                        print_summary=False, time_factor=1, memory_factor=4, success_email=False)
        # break
    submit_all_jobs(as_array=True)
