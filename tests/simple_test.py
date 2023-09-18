#%%
import adddeps
from utils.utils import get_simulation_class
import os
from settings import HDF5_PATH
from simulator import SimulatorLennard, SimulatorLennardLammps
params_model = {
    "group_name" : "just test",
    "cls":"SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.15,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy": 1,
    "sigma_grid":0.15,
    "position_random_shift_percentage": 0.0/100,
    "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 100,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    "run_lammps":False
}

if __name__ == "__main__":
    print(HDF5_PATH)
    sim_class_name = params_model.pop("cls", "SimulatorMagnetic")

    SimulatorClass = get_simulation_class(sim_class_name)

    params_model["name"] = params_model.get("name", os.getenv("HOSTNAME"))

    sim : SimulatorLennardLammps = SimulatorClass(**params_model)

    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)
    print(sim.get_simulation_command())
    # sim.push_hdf5()
###############
# /data/biophys/ashmat/builds/LAMMPS/mylammps/builds/build_flora10/lmp -sf omp -in "./tmp_lammps/4bcd9f971cf0f2da.in"
# .lammps_build/lmp -sf omp -in "./tmp_lammps/4bcd9f971cf0f2da.in"
# %%
