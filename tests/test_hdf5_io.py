import unittest

import numpy as np
import os
from simulator import SimulatorLennardLammps, SimulatorMagnetic, SimulatorLennard
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
    "sigma_grid":0.5,
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
    
    @unittest.skip("reason for skipping")
    def test_io_hdf5(self):
        sim = SimulatorMagnetic(**params_model)
        init = sim.init_positions_velocities(**params_init)
        history = sim.simulate(0.03, dt=1e-3, record_interval=2e-3, algorithm="VERLET")

        sim1 = SimulatorMagnetic(**params_model)
        sim1.r_init, sim1.v_init = init
        history1 = sim1.simulate(0.01, dt=1e-3, record_interval=2e-3, algorithm="VERLET")
        # history11 = sim.to_array(sim1.simulate(0.02, dt=1e-5, record_interval=1e-3, algorithm="VERLET"))
        path = sim1.push_hdf5()
        print("path:", path)
        self.files_to_delete.append(path)

        sim2 = SimulatorMagnetic()
        sim2.load(hdf5_path=path)
        history2 = sim2.simulate(0.02, dt=1e-3, record_interval=2e-3, algorithm="VERLET")

        self.assertTrue(np.allclose(history2["rs"], history["rs"]))


    def test_lammps_parsing(self):
        sim_lammps = SimulatorLennardLammps(**params_model)
        init = sim_lammps.init_positions_velocities(**params_init)
        sim_lammps.simulate(0.03, dt=1e-3, record_interval=2e-3, warmup=0.0,
                            particle_properties=True,
                            total_properties=True)
        print("###################################")
        print("### command")
        print(sim_lammps.get_simulation_command())
        print("###################################")

        history_lammps = sim_lammps.history

        sim = SimulatorLennard(**params_model)
        sim.history.extend(history_lammps.size())
        for i in range(history_lammps.size()):
            sim.stamp_history(history_lammps["rs"][i],
                              history_lammps["vs"][i],
                              history_lammps["time"][i],
                              particle_properties=True,
                              total_properties=True)
        history = sim.history
        history.pop("collisions")
        # print(sorted(history_lammps.keys()))
        # print(sorted(history.keys()))
        
        self.assertTrue(len(history_lammps) == len(history))

        for key in history_lammps:
            if key in ["LJ_force", "IE", "total/IE",  "total/E"]:
                continue
            # print("--",key)
            # print(np.abs(history_lammps[key]-history[key]).mean())
            self.assertTrue(np.allclose(history_lammps[key], history[key],rtol=1e-5, atol=1e-4))

    def test_particle_to_total_property_conversion(self):
        sim_lammps = SimulatorLennardLammps(**params_model)
        init = sim_lammps.init_positions_velocities(**params_init)
        sim_lammps.simulate(0.03, dt=1e-3, record_interval=2e-3, warmup=0.0,
                            particle_properties=True,
                            total_properties=True)
        h5_output_path = sim_lammps.push_hdf5()
        history = sim_lammps.history

        from utils.convert import convert_particle_prop_to_total_prop

        new_history = convert_particle_prop_to_total_prop(h5_output_path)

        for key in history:
            if "total" in key:
                # print("--", key)
                # print(history[key])
                # print(new_history[key])
                self.assertTrue(np.allclose(history[key], new_history[key],
                                            rtol=1e-5, atol=1e-5))


    @unittest.skip("reason for skipping")
    def test_io_db(self):
        sim = SimulatorMagnetic(**params_model)
        init = sim.init_positions_velocities(**params_init)
        history = sim.simulate(0.03, dt=1e-3, record_interval=2e-3, algorithm="VERLET")

        sim1 = SimulatorMagnetic(**params_model)
        sim1.r_init, sim1.v_init = init
        history1 = sim1.simulate(0.01, dt=1e-3, record_interval=2e-3, algorithm="VERLET")
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
