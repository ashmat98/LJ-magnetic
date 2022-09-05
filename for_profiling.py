import numpy as np

from simulator.magnetic import SimulatorMagnetic

params_model = {
    "R" : 1.0,
    "Rz" : 0.5,
    "Bz" : 1.0,
    "eccentricity": 0.01,
    "sigma":0.5,
    "epsilon":1.0
}
params_init = {
    "energy": 1.0,
    "sigma_grid":0.6,
    "position_random_shift_percentage": 0.0/100,
    "planar": False,
    "zero_momentum": True,
}
params_simulation = {}

sim = SimulatorMagnetic(**params_model)
r_init = sim.init_positions_closepack(**params_init)
params_init["angular_momentum"] = sim.L_given_E_constraint(params_init["energy"])[0]*0.75
v_init = sim.init_velocities(**params_init)
print(sim.particle_number())
history = sim.simulate(1, dt=1e-5, record_interval=1e-4, algorithm="VERLET")
