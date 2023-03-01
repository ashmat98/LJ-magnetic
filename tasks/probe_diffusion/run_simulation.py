
from utils.logs import get_stdout_logger
from simulator.magnetic import SimulatorMagnetic


params_model = {
    "group_name" : "BEnsemble 1",
    "R" : 1.0,
    "Rz" : 0.1,
    "eccentricity": 0.15,
    "sigma":0.5,
    "epsilon":1.0,
    "get_logger" : get_stdout_logger
}
params_init = {
    "energy": 1.0,
    "sigma_grid":0.55,
    "position_random_shift_percentage": 1.0/100,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 1000,
    "dt" : 1e-4,
    "record_interval" : 1e-1,
    "algorithm" : "VERLET",
    # "before_step" : before_step
}

sim = SimulatorMagnetic(Bz=1e-6, **params_model)
sim.init_positions_closepack(**params_init)
sim.init_velocities(**params_init)
