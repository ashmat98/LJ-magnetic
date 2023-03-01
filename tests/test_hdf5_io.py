import unittest

import numpy as np
import os
from simulator.magnetic import SimulatorMagnetic
from settings import HDF5_PATH

params_model = {
    "R" : 1.0,
    "Rz" : 0.5,
    "Bz" : 1.0,
    "eccentricity": 0.01,
    "sigma":0.1,
    "epsilon":1.0
}
params_init = {
    "energy": 1.0,
    "sigma_grid":0.2,
    "position_random_shift_percentage": 0.0/100,
    "planar": False,
    "zero_momentum": True
}
params_simulation = {}


class hdf5_IO_Test(unittest.TestCase):
    files_to_delete = []

    @classmethod
    def tearDownClass(cls):
        for file in cls.files_to_delete:
            if os.path.exists(file):
                os.remove(file)
                pass
    
    # @unittest.skip("reason for skipping")
    def test_io_hdf5(self):
        sim = SimulatorMagnetic(**params_model)
        init = sim.init_positions_velocities(**params_init)
        history = sim.to_array(sim.simulate(0.03, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))

        sim1 = SimulatorMagnetic(**params_model)
        sim1.r_init, sim1.v_init = init
        history1 = sim.to_array(sim1.simulate(0.01, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))
        # history11 = sim.to_array(sim1.simulate(0.02, dt=1e-5, record_interval=1e-3, algorithm="VERLET"))
        path = sim1.push_hdf5()
        print("path:", path)
        self.files_to_delete.append(path)

        sim2 = SimulatorMagnetic()
        sim2.load(hdf5_path=path)
        history2 = sim2.to_array(sim2.simulate(0.02, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))

        self.assertTrue(np.allclose(history2["rs"], history["rs"]))

    # @unittest.skip("reason for skipping")
    def test_io_db(self):
        sim = SimulatorMagnetic(**params_model)
        init = sim.init_positions_velocities(**params_init)
        history = sim.to_array(sim.simulate(0.03, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))

        sim1 = SimulatorMagnetic(**params_model)
        sim1.r_init, sim1.v_init = init
        history1 = sim.to_array(sim1.simulate(0.01, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))
        # history11 = sim.to_array(sim1.simulate(0.02, dt=1e-5, record_interval=1e-3, algorithm="VERLET"))
        hsh = sim1.hash()

        sid = sim1.push_db()
        print(hsh)
        self.files_to_delete.append(
            os.path.join(HDF5_PATH, hsh + ".hdf5"))
        print("sid:", sid)

        sim2 = SimulatorMagnetic()
        sim2.load(id=sid)
        history2 = sim2.to_array(sim2.simulate(0.02, dt=1e-3, record_interval=2e-3, algorithm="VERLET"))

        self.assertTrue(np.allclose(history2["rs"], history["rs"]))
