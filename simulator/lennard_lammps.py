import datetime
import pandas as pd
import numpy as np
from simulator.lennard import SimulatorLennard
from simulator.hdf5IO import Simulation
import os
import time
import hashlib
import h5py


class SimulatorLennardLammps(SimulatorLennard):
    def __init__(self, **kwargs):
        __load = kwargs.pop("__load", True)

        super().__init__(__load=False, **kwargs)

        os.makedirs("./tmp_lammps", exist_ok=True)
        self._hash = self._hash_init()
        self._config_path = os.path.join("./tmp_lammps", self._hash)
        self._precision = 6

        if __load:
            self.load(**kwargs)

    def _hash_init(self):
        hashable = (self.id, self.name, self.group_name, os.getpid())
        hashable_str = tuple(str(x) for x in hashable)
        return hashlib.md5("".join(hashable_str).encode()).hexdigest()[::2]

    def _generate_data_file(self):
        N = self.particle_number()
        a, b, c = self.abc
        a = a * 10
        b = b * 10
        c = c * 10

        lines = [
            "LAMMPS data file",
            f"{N} atoms",
            "1 atom types",
            "\n",
            f"{-a} {a} xlo xhi",
            f"{-b} {b} ylo yhi",
            f"{-c} {c} zlo zhi",
            "\n",
        ]

        lines.append("Atoms\n")
        for i, r in zip(range(N), self.r_init.T):
            lines.append(
                "{1} 1 {2:0.{0}} {3:0.{0}} {4:0.{0}}".format(
                    self._precision, i+1, *r
                )
            )

        lines.append("\nVelocities\n")
        for i, v in zip(range(N), self.v_init.T):
            lines.append(
                "{1} {2:0.{0}} {3:0.{0}} {4:0.{0}}".format(
                    self._precision, i+1, *v
                )
            )

        file_name = self._config_path + ".data"

        with open(file_name, "w") as f:
            f.write("\n".join(lines))

    def _generate_config_file(self, dt, steps, warmup_steps, record_steps, 
                              particle_properties, total_properties, output_particles):
        file_name = self._config_path + ".in"
        with open("simulator/lammps_scripts/template.in") as f:
            template = f.read()

        kx, ky, kz = 1/self.abc**2

        lines = [
            f"variable warmup_steps equal {warmup_steps}",
            f"variable steps equal {steps}",
            f"variable record_steps equal {record_steps}",
            # Define the initial potential parameters
            f"variable kx_warmup equal {(kx+ky)/2}",
            f"variable ky_warmup equal {(kx+ky)/2}",
            f"variable kz_warmup equal {kz}",
            # Define the new potential parameters
            f"variable kx equal {kx}",
            f"variable ky equal {ky}",
            f"variable kz equal {kz}",
            # define LJ parameters
            f"variable sigma equal {self.sigma}",
            f"variable epsilon equal {self.epsilon/4}",
            # hash that appears in
            f"variable hash string \"{self._hash}\"",

            # Set the timestep
            f"\nvariable dt equal {dt}",
            f"\nvariable nb_rebuild equal {int(0.03/dt)}",
            f"variable particles equal {self.particle_number()}",
            f"variable output_particles equal {output_particles}",

            # Output properties
            f"\nvariable particle_properties string \"{particle_properties}\"",
            f"variable total_properties string \"{total_properties}\"",



            "\n",
        ]
        with open(file_name, "w") as f:
            f.write("\n".join(lines))
            f.write(template)

    def iteration_time_estimate(self, n):
        """
        time needed for single iteration.
        n : particle number
        """
        return datetime.timedelta(seconds=np.maximum(2e-3, 1.0e-6 * n**1 * 3))

    def simulate(self, iteration_time=1.0, dt=0.0005, record_interval=0.01, warmup=0,
                 run_lammps=True,
                 particle_properties=True,
                 total_properties=False,
                 output_particles=None):

        self.start_time = datetime.datetime.now()

        self.dt = dt
        self.record_interval = record_interval

        steps = int(iteration_time / dt)
        warmup_steps = int(warmup / dt)
        record_steps = int(record_interval / dt)
        if output_particles is None:
            output_particles = self.particle_number()


        self._generate_config_file(
            dt, steps, warmup_steps, record_steps, 
            particle_properties, total_properties, output_particles)
        self._generate_data_file()

        print("LAMMPS command:")
        print(self.get_simulation_command())
        if run_lammps:
            os.system(self.get_simulation_command())
            print("Simulation has finished!")
            print("Processing the dump files...")

            records_alloc = (steps+warmup_steps)//record_steps + 3

            if particle_properties:
                self._load_particle_properties(records_alloc, output_particles)
            if total_properties:
                self._load_total_properties(records_alloc)

        self.finish_time = datetime.datetime.now()

    def get_simulation_command(self):
        # return f".lammps_build/lmp  -in \"{self._config_path}.in\""

        return f".lammps_build/lmp -sf omp -in \"{self._config_path}.in\""

    def other_metrics(self, r, v, t):
        metrics = super().other_metrics(r, v, t)

        return metrics

    def get_data_frames(self, **kwargs):
        dframes = super().get_data_frames(**kwargs)

        return dframes

    def create_item(self):
        item: Simulation = super().create_item()

        return item

    def apply_item(self, item: Simulation):
        super().apply_item(item)


    # @staticmethod
    # def parce_lammpstrj_with_rv(lammpstrj, particles, records_alloc):
    #     f = open(lammpstrj, "r")
    #     entries = ["x","y","z","vx","vy","vz", "KE", "PE", "IE", "Lx", "Ly", "Lz"]

    #     data = np.zeros(shape=(records_alloc*particles, len(entries)))

    #     print(particles)

    #     _i = 0

    #     for line in iter(f.readline, ''):
    #         #         line = f.readline()
    #         print(line)
    #         if "ATOMS" == line[6:11]:
    #             for i in range(particles):
    #                 line = list(map(float, f.readline().strip().split()))

    #                 data[_i, :] = line
    #                 _i += 1
    #     f.close()
    
    #     data = data[:_i].reshape(-1, particles, len(entries))

    #     rs = data[:,:,0:3].transpose(0,2,1)
    #     vs = data[:,:,3:6].transpose(0,2,1)
        

    #     history = {key: data[:, :, i] for i, key in enumerate(entries[6:])}
    #     history["L"] = np.stack(
    #         [history.pop("Lx"), history.pop("Ly"), history.pop("Lz")], axis=1)

    #     return history, rs, vs
    
    # def _load_particle_properties_rv(self, records_alloc, output_particles):
    #     history = dict()

    #     lammpstrj = self._config_path + ".lammpstrj"

    #     data, history["rs"], history["vs"] = self.parce_lammpstrj_with_rv(
    #         lammpstrj, output_particles, records_alloc)
        
    #     history["time"] = np.round(np.arange(len(history["rs"])) * self.record_interval,5)

    #     history.update(data)

    #     self.history.update(history)

    @staticmethod
    def parce_lammpstrj(lammpstrj, particles, records):
        f = open(lammpstrj, "r")
        entries = ["KE", "PE", "IE", "Lx", "Ly", "Lz"]

        data = np.zeros(shape=(records*particles, len(entries)))
        _i = 0

        for line in iter(f.readline, ''):
            #         line = f.readline()
            if "ATOMS" == line[6:11]:
                for i in range(particles):
                    line = list(map(float, f.readline().strip().split()))

                    data[_i, :] = line
                    _i += 1
        f.close()

        data = data.reshape(records, particles, len(entries))
        history = {key: data[:, :, i] for i, key in enumerate(entries[:3])}
        history["L"] = data[:,:,3:6].transpose(0,2,1)
        # history["L"] = np.stack(
        #     [history.pop("Lx"), history.pop("Ly"), history.pop("Lz")], axis=1)

        return history

    def _load_particle_properties(self, records_alloc, output_particles):
        h5md = self._config_path + ".h5"
        history = dict()
        with h5py.File(h5md) as ds:
            history["rs"] = ds["particles/my_subset/position/value"][:
                                                               ].transpose(0, 2, 1)
            history["vs"] = ds["particles/my_subset/velocity/value"][:
                                                               ].transpose(0, 2, 1)
            history["LJ_force"] = ds["particles/my_subset/force/value"][:
                                                                  ].transpose(0, 2, 1)

            history["time"] = ds["particles/my_subset/force/time"][:]

        records, _, particles = history["rs"].shape

        lammpstrj = self._config_path + ".lammpstrj"
        history.update(self.parce_lammpstrj(lammpstrj, particles, records))

        self.history.update(history)

    def _load_total_properties(self, records_alloc):
        total_lammpstrj = self._config_path + ".total.lammpstrj"
        self.history.update(self.parce_total_lammpstrj(
            total_lammpstrj, records_alloc))

    @staticmethod
    def parce_total_lammpstrj(total_lammpstrj, records):
        f = open(total_lammpstrj, "r")
        entries = ["step", "time", "total/KE", "total/PE", "total/IE", "total/E",
                   "total/L", "total/xx", "total/yy", "total/zz", "total/xy",
                   "total/vxvx", "total/vyvy", "total/vzvz", "total/vxvy",
                   "total/omega_MLE", "total/beta_MLE"]

        data = np.zeros(shape=(records, len(entries)))
        _i = 0

        _header = f.readline()

        for line in iter(f.readline, ''):
            data[_i, :] = list(map(float, line.strip().split()))
            if _i == 0 or data[_i, 0] != data[_i-1, 0]:
                _i += 1
        f.close()

        history = {key: data[:_i, i_entry]
                   for i_entry, key in enumerate(entries)}
        history.pop("step")

        return history
