from asyncio.log import logger
from code import interact
import numbers
from selectors import EpollSelector
import time

import numpy as np
from collections import defaultdict
# from tqdm.autonotebook import tqdm
from tqdm import tqdm

import os
import datetime
import logging
import os

from utils.utils import get_function, iteration_time_estimate, memory_estimate


def _init_history(self):
    self._history_ptr = 0
    self.history = defaultdict(list)

    def add_field(key, value):
        self.history[key] = np.zeros(shape=(1,) + value.shape, dtype="float32")
        self.history[key][0] = value

    add_field("time", np.array(0))
    add_field("rs", self.r_init)
    add_field("vs", self.v_init)
    for key, value in self.other_metrics(self.r_init, self.v_init, 0).items():
        add_field(key, value)

    self._history_ptr = 1


def _extend_history(self, size):
    ptr = self._history_ptr

    def extend_field(key):
        old_array = self.history[key]
        new_array = np.append(old_array[:ptr],
                              np.zeros(shape=(size,) +
                                       old_array.shape[1:], dtype="float32"),
                              axis=0)
        self.history[key] = new_array
        del old_array

    for key in self.history:
        extend_field(key)


class HistoryDict(dict):
    def __init__(self, **kwargs):
        self._alloc_size = 0
        self._ptr = 0
        self._dtype = "float32"

        if len(kwargs) > 0:
            self._alloc_size = len(kwargs[next(kwargs)])

        self.ptr = self._alloc_size

        super().__init__(kwargs)

    def new_stamp(self):
        self._ptr += 1

    def push(self, key, value):
        if key not in self:
            self[key] = np.zeros(shape=(self._alloc_size,) +
                                 value.shape, dtype=self._dtype)

        self[key][self._ptr-1] = value

    def top(self, key):
        return self[key][self._ptr-1]

    def extend(self, size):
        self._alloc_size = self.size() + size

        def extend_field(key):
            old_array = self.get(key)
            new_array = np.append(
                old_array, np.zeros(shape=(size,) + old_array.shape[1:],
                                    dtype="float32"), axis=0)
            self[key] = new_array
            del old_array

        for key in self:
            extend_field(key)

    def size(self):
        return self._ptr

    def get(self, key, default=None):
        if key in self:
            return self[key][:self._ptr]
        return default

    def update(self, dct):
        for key, value in dct.items():
            if self._alloc_size == 0:
                self._alloc_size = len(value)
                self._ptr = self._alloc_size

            assert len(value) == self._alloc_size
            self[key] = value


class SimulatorBase:
    def __init__(self, verbose=True, **kwargs):
        np.random.seed((os.getpid() * int(time.time())) % 123456789)

        self.dt = None
        self.history: HistoryDict = HistoryDict()
        self._history_ptr = 0        # index of possition, where new item should be stored
        self._history_size = 0        # current ated size of history

        self.history_arr = None
        self.history_essential = None

        self.r_init = None
        self.v_init = None
        self.collision_state = dict()
        self.collision_count = dict()

        self.EPS = 1e-8
        self.record_interval = None

        self.start_time = None
        self.finish_time = None
        # self.client = Client()
        self.step = None

        # temporary
        self.dt2 = None
        self.last_a = None

        self.last_r_diff = None
        self.last_r_dist = None

        self.get_logger = logging.getLogger

        self.verbose = verbose

        self._simulation_t = 0

    def iteration_time_estimate(self, n):
        return iteration_time_estimate(n)

    def norm(self, r):
        return np.sqrt(np.sum(r**2, axis=0))

    def calc_diff(self, r, with_nan=False):
        """
        r is a 3xN ndarray
        returns matrix NxNx: d
        d[i,j] = r[i] - r[j]
        note that this is antisymmetric matrix
        """
        D = r[:, :, None] - r[:, None, :]

        if with_nan:
            np.fill_diagonal(D[0], np.nan)
            np.fill_diagonal(D[1], np.nan)
            np.fill_diagonal(D[2], np.nan)

        self.last_r_diff = D

        return D

    def calc_dist(self, r):
        """
        r is a 3xN ndarray
        returns matrix NxNx: d
        d[i,j] = ||r[i] - r[j]||
        note that this is symmetric matrix
        returns matrix of distancec
        """
        diff = self.calc_diff(r)
        return self.norm(diff)

    def calc_acceleration(self, r, v, t):
        raise NotImplementedError

    def kinetic_energy(self, r, v):
        return 0.5 * np.sum(v**2, axis=0)

    def external_potential_energy(self, r, v):
        raise NotImplementedError

    def interaction_energy(self, r, v):
        raise NotImplementedError

    def angular_momentum(self, r, v) -> np.ndarray:
        return np.cross(r.T, v.T).T

    def moment_of_inertia_z(self, r, v):
        return np.square(self.norm(r[:2]))

    def angular_velocity(self, r, v):
        return np.cross(r.T, v.T).T / (self.EPS + np.sum(r**2, axis=0))

    def system_energy(self, r, v):
        KE = self.kinetic_energy(r, v)
        PE = self.external_potential_energy(r, v)
        IE = self.interaction_energy(r, v)
        return KE, PE, IE

    def total_energy(self, r, v, KE=None, PE=None, IE=None):
        KE1, PE1, IE1 = self.system_energy(r, v)
        if KE is None:
            KE = KE1
        if PE is None:
            PE = PE1
        if IE is None:
            IE = IE1
        return (PE + KE + 0.5 * IE).sum()

    def estimmate_temperature(self, vs):
        raise NotImplementedError
        vs = np.asarray(vs)
        KE_mean = np.sum(vs**2)/2/vs.shape[0]
        return KE_mean*2/(3 * vs.shape[1])

    def pressure_viral(self, rs, vs):
        raise NotImplementedError

        vs = np.asarray(vs)
        rs = np.asarray(rs)
        KE_mean = np.sum(vs**2)/2/vs.shape[0]
        W_int = np.mean([np.sum(LJ_potential_derivative(r, box) * calc_dist(r, box))
                        for r in rs])
        pressure = 1/np.product(box) * (KE_mean * (2/3) - 1/6 * W_int)
        return pressure

    def forget_history(self):
        self.history = None

    def get_history(self):
        new_history = {}
        for key in self.history:
            new_history[key] = self.history.get(key)

        return new_history

        # if self.history_arr is None or len(self.history["rs"]) != len(self.history_arr["rs"]):
        #     self.history_arr = self.to_array(self.history)
        # return self.history_arr

    def get_data_frames(self, **kwargs):
        if "record_interval" in kwargs:
            self.record_interval = kwargs["record_interval"]
        index = np.arange(0, self.history.size()) * self.record_interval
        dframes = dict()
        dframes["index"] = index
        return dframes

    def set_history(self, history):
        self.history = self.to_list(history)

    def particle_number(self):
        if self.r_init is not None:
            return self.r_init.shape[1]
        else:
            return 0

    def next_time(self, t):
        return round(t+self.dt, 7)

    def init_positions_closepack(self, energy, sigma_grid,
                                 position_random_shift_percentage, planar, **kwargs):

        # sometimes we want to initialise positions with different energy
        energy = kwargs.get("energy_for_position_init", energy)

        v1 = np.array([0.5*np.sqrt(3), 0.5, 0])
        v2 = np.array([0.5*np.sqrt(3), -0.5, 0])
        v3 = np.array([np.sqrt(1/3), 0, np.sqrt(2/3)])

        bounds = np.sqrt(energy * 2 * self.abc**2)
        if planar:
            bounds[2] = self.EPS
        n3 = round(1+bounds[2]/v3[2])
        n1 = n2 = round(max(bounds[0], bounds[1])*2+1)

        def helper(x):
            return np.concatenate([-x[::-1][:-1], x])
        grid_points = [helper(np.arange(0, bnd))
                       for bnd in np.array([n1, n2, n3])/sigma_grid]
        integer_points = np.stack(np.meshgrid(*grid_points)).reshape(3, -1)
        points = sigma_grid * np.array([v1, v2, v3]).T.dot(integer_points)

    #     r_init = points
        r_init = points[:, self.external_potential(points) < energy]

        shift_eps = max(0, (sigma_grid-self.sigma)*0.5 *
                        position_random_shift_percentage)
        r_init += np.random.uniform(-shift_eps, shift_eps, r_init.shape)
        self.r_init = r_init
        return r_init

    def L_given_E_constraint(self, energy):
        N = self.particle_number()

        P0 = (self.external_potential_energy(self.r_init, None).sum()
              + 0.5*self.interaction_energy(self.r_init, None).sum())
        E1 = N * energy - P0
        I0 = self.moment_of_inertia_z(self.r_init, None).sum()
        return np.sqrt(2*I0*E1), E1

    def init_velocities(self, energy, angular_momentum=None, angular_momentum_factor=None, **kwargs):

        if angular_momentum_factor is not None:
            angular_momentum = self.L_given_E_constraint(
                energy)[0]*angular_momentum_factor
        if angular_momentum is None:
            raise Exception("Angular momentum is not provided")

        self.v_init = np.random.randn(*self.r_init.shape)

        E0 = self.kinetic_energy(None, self.v_init).sum()
        I0 = self.moment_of_inertia_z(self.r_init, None).sum()
        L0 = np.sum(self.angular_momentum(self.r_init, self.v_init)[-1])
        L1 = angular_momentum
        L1_max, E1 = self.L_given_E_constraint(energy)
        assert L1_max > L1

        alpha1 = -(np.sqrt(2*E1*I0 - L1**2)/np.sqrt(2*E0*I0 - L0**2))
        omega1 = ((-2*E1*I0*L0 + L0*L1**2 - (2*E0*I0*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2) +
                   (L0**2*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2))/(2*E1*I0**2 - I0*L1**2))
        alpha2 = np.sqrt(2*E1*I0 - L1**2)/np.sqrt(2*E0*I0 - L0**2)
        omega2 = ((-2*E1*I0*L0 + L0*L1**2 + (2*E0*I0*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2) -
                   (L0**2*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2))/(2*E1*I0**2 - I0*L1**2))
        omega2 = (-L0 + (np.sqrt(2*E0*I0 - L0**2)*L1) /
                  np.sqrt(2*E1*I0 - L1**2))/I0
        self.v_init = alpha2 * \
            (self.v_init + np.cross([0, 0, omega2], self.r_init.T).T)
        return self.r_init, self.v_init, E1

    def init_positions_velocities(self, energy, sigma_grid,
                                  position_random_shift_percentage, planar, zero_momentum, **kwargs):
        def helper(x):
            return np.concatenate([-x[::-1][:-1], x])
        bounds = np.sqrt(energy * 2 * self.abc**2)
        if planar:
            bounds[2] = self.EPS

        grid_points = [helper(np.arange(0, bnd, sigma_grid)) for bnd in bounds]
        points = np.stack(np.meshgrid(*grid_points)).reshape(3, -1)
        points += np.random.randn(*points.shape) * \
            position_random_shift_percentage * sigma_grid
        r_init = points[:, self.external_potential(points) < energy]
        N = r_init.shape[1]

        kinetic = (energy - self.external_potential(r_init))
        v_mag = np.sqrt(2 * kinetic)

        v_init = np.random.randn(3, N)
        if planar:
            v_init[2, :] = 0
        v_init = v_init / self.norm(v_init) * v_mag

        if zero_momentum:
            v_init = v_init - v_init.mean(axis=1, keepdims=True)

        self.r_init = r_init
        self.v_init = v_init

        return r_init, v_init

    def reorient_velocities(self):
        for i in range(self.particle_number()):
            v = self.v_init[:, i]
            v_mag = self.norm(v)
            v_new = np.random.randn(3)
            v_new = v_new / self.norm(v_new) * v_mag
            self.v_init[:, i] = v_new

    def rotational_push(self, p):
        for i in range(self.particle_number()):
            r, v = self.r_init[:, i], self.v_init[:, i]
            r_plane = self.norm(r[:2])
            e_perp = np.array([-r[1], r[0], 0])/(r_plane + self.EPS)
            e_par = np.array([r[0], r[1], 0])/(r_plane + self.EPS)
            e_z = np.array([0, 0, 1])

            v_mag = self.norm(v)
            v_perp_mag = np.dot(v, e_perp)
            v_not_perp = v - v_perp_mag * e_perp
            v = (v_mag * np.sqrt(p) * e_perp
                 + v_not_perp * np.sqrt((1-p)) * v_mag / (self.norm(v_not_perp) + self.EPS))

            self.v_init[:, i] = v

    def rotational_push_2(self, p):
        for i in range(self.particle_number()):
            r, v = self.r_init[:, i], self.v_init[:, i]
            r_mag = np.sqrt((r[0]**2 + r[1]**2))
            v_mag = self.norm(v)
            omega = v_mag*r_mag/(r_mag**2 + self.EPS)
            v = v * (1-p) + p * np.array([-r[1]*omega, r[0]*omega, 0])
            self.v_init[:, i] = v

    def other_metrics(self, r, v, t):
        return dict()

    @staticmethod
    def to_array(dct):
        dct = dct.copy()
        for key, value in dct.items():
            dct[key] = np.array(value, dtype=np.float32)
        return dct

    @staticmethod
    def to_list(dct):
        dct = dct.copy()
        for key, value in dct.items():
            dct[key] = list(value)
        return dct

    def update_step_function(self, algorithm):
        if algorithm == "EULER":
            self.step = self.step_EULER
        elif algorithm == "RK":
            self.step = self.step_RK
        elif algorithm == "VERLET":
            self.step = self.step_VERLET

    def step_EULER(self, r, v, t):
        a = self.calc_acceleration(r, v, t)
        r += v * self.dt
        v += a * self.dt
        return r, v, self.next_time(t)

    def step_RK(self, r, v, t):
        dt = self.dt
        hdt = 0.5 * dt

        k1v = self.calc_acceleration(r, v, t)
        k1r = v

        k2v = self.calc_acceleration(r + hdt, v + hdt * k1v, t + hdt)
        k2r = v + hdt * k1v

        k3v = self.calc_acceleration(r + hdt * k2r, v + hdt * k2v, t + hdt)
        k3r = v + hdt * k2v

        k4v = self.calc_acceleration(r + dt * k3r, v + dt * k3v, t + dt)
        k4r = v + dt * k3v

        return (
            r + (k1r+2*k2r+2*k3r+k4r)*dt/6,
            v + (k1v+2*k2v+2*k3v+k4v)*dt/6,
            self.next_time(t)
        )

    def step_VERLET(self, r, v, t):
        if self.last_a is None:
            self.last_a = self.calc_acceleration(r, v, t)

        v_half = v + 0.5 * self.last_a * self.dt
        r = r + v_half * self.dt
        t = self.next_time(t)
        self.last_a = self.calc_acceleration(r, v, t)
        v = v_half + 0.5 * self.last_a * self.dt
        return r, v, t

    def collision_init(self):
        for k in [1, 1.061, 1.122]:
            self.collision_state[k] = np.zeros(
                (self.particle_number(), self.particle_number()), dtype=int)
            self.collision_count[k] = 0

    def collision_update(self, r):
        pass

    def before_simulation(self, r, v, t, algorithm):
        if self.history.size() == 1:
            self.start_time = datetime.datetime.now()

    
    def simulate_estimate(self, iteration_time=1.0, dt=0.0005, record_interval=0.01,
                          algorithm="EULER", before_step=None, N=None, **kwargs):
        if N is None:
            N = self.particle_number()
        estimated_time = self.iteration_time_estimate(N)*iteration_time/dt
        estimated_time = datetime.timedelta(
            seconds=int(estimated_time.total_seconds()))
        return {
            "time": estimated_time,
            "memory": memory_estimate(N) * iteration_time / record_interval
        }

    def stamp_history(self, r, v, t, particle_properties, total_properties):
        self.history.new_stamp()

        metrics = self.other_metrics(r, v, t)

        self.history.push("time", t)

        if particle_properties:
            self.history.push("vs", v)
            self.history.push("rs", r)

            for key, value in metrics.items():
                self.history.push(key, value)

        if total_properties:
            prefix = "total/"
            # self.history.push(prefix+"Iz", np.sum(r[0]**2 + r[1]**2, axis=-1))

            self.history.push(prefix+"xx", np.mean(r[0]**2, axis=-1))
            self.history.push(prefix+"yy", np.mean(r[1]**2, axis=-1))
            self.history.push(prefix+"zz", np.mean(r[2]**2, axis=-1))
            self.history.push(prefix+"xy", np.mean(r[0] * r[1], axis=-1))

            self.history.push(prefix+"vxvx", np.mean(v[0]**2, axis=-1))
            self.history.push(prefix+"vyvy", np.mean(v[1]**2, axis=-1))
            self.history.push(prefix+"vzvz", np.mean(v[2]**2, axis=-1))
            self.history.push(prefix+"vxvy", np.mean(v[0] * v[1], axis=-1))

            omega_MLE = (np.mean(r[0] * v[1]-r[1] * v[0]) /
                         np.mean(r[0]**2+r[1]**2))

            beta_MLE = (1/3 * np.mean(
                (v[0]+omega_MLE * r[1])**2 +
                (v[1]-omega_MLE * r[0])**2 + (v[2])**2
            ))**-1

            self.history.push(prefix+"omega_MLE", omega_MLE)
            self.history.push(prefix+"beta_MLE", beta_MLE)

            self.history.push(prefix+"L", metrics["L"][2].sum())
            self.history.push(prefix+"KE", np.sum(metrics["KE"]))
            self.history.push(prefix+"IE", np.sum(metrics["IE"]))
            self.history.push(prefix+"PE", np.sum(metrics["PE"]))

            # np.sum(0.5 * history["IE"] + history["PE"] + history["KE"]
            self.history.push(prefix+"E",
                              self.history.top(prefix+"KE")
                              + self.history.top(prefix+"PE")
                              + 0.5 * self.history.top(prefix+"IE")
                              )

            if "collisions" in metrics:
                for i, c in enumerate(metrics["collisions"]):
                    self.history.push(prefix+f"collisions-{i+1}", c)

    def simulate(self, iteration_time=1.0, dt=0.0005, record_interval=0.01,
                 algorithm="EULER",
                 before_step=None,
                 particle_properties=True,
                 total_properties=False
                 ):
        """
        r,v,a,t: initial parameters of the system
        box: size of the box
        history: previous recordings, give if you wwant to continue simulation
        iteration_time: time to simulate
        dt: time interval of the one step
        record_interval: interval of recording the state of the system 
        """
        assert isinstance(iteration_time, numbers.Number)
        assert isinstance(dt, numbers.Number)

        np.random.seed((os.getpid() * int(time.time())) % 123456789)

        logger = self.get_logger()

        self.dt = dt
        self.dt2 = dt * dt
        self.record_interval = record_interval
        self.collision_init()

        if type(before_step) is str:
            before_step = get_function(before_step)

        alloc_size = int(iteration_time/record_interval + 3)
        self.history.extend(alloc_size)

        if self.history.size() == 0:
            self.stamp_history(self.r_init, self.v_init, np.array(0),
                               particle_properties, total_properties)
            r = self.r_init.copy()
            v = self.v_init.copy()
        else:
            r = self.history.top("rs").astype("float64")
            v = self.history.top("vs").astype("float64")

        self._simulation_t = t = self.history.top("time").astype("float64")

        if "collisions" in self.history:
            for _key, _val in zip(self.collision_count, self.history.top("collisions")):
                self.collision_count[_key] = _val

        self.before_simulation(r, v, t, algorithm)
        self.update_step_function(algorithm)

        logger.info(f"starting simulation {self.name} {self.group_name}")

        last_stored_time = t

        for it in tqdm(range(int((iteration_time+self.EPS)/dt)),
                       mininterval=1, disable=not self.verbose):
            if before_step is not None:
                before_step(self, r, v, t)

            r, v, t = self.step(r, v, t)
            self._simulation_t = t
            self.collision_update(r)

            if t - last_stored_time >= record_interval - dt/4:

                last_stored_time = round(last_stored_time + record_interval, 6)
                self.stamp_history(r, v, last_stored_time,
                                   particle_properties, total_properties)

        self.finish_time = datetime.datetime.now()

        return self.get_history()
