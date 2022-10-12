from relaxation.estimators import RelaxationFinder
from simulator.magnetic import SimulatorMagnetic
from utils.logs import get_logger


params_model = {
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 1.0,
    "eccentricity": 0.0,
    "epsilon":1.0,
    "get_logger" : get_logger,
    "verbose" : False
}
params_init = {
    "energy": 1.0,
    "sigma_grid":0.75,
    "position_random_shift_percentage": 50.0/100,
    "planar": False,
    "zero_momentum": True,
    "angular_momentum_factor" : 0.7
}
params_simulation = {
    "iteration_time" : 100,
    "dt" : 1e-3,
    "record_interval" : 1e-2,
    "algorithm" : "VERLET"
}

def f(sigma):
    params_model["sigma"] = sigma
    sim = SimulatorMagnetic(**params_model)
    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)
    rf = RelaxationFinder(sim, tmax=50, verbose=False)
    summary = rf.summarize()
    summary["sigma"] = sim.sigma
    return summary





