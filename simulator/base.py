from asyncio.log import logger
import pickle
from selectors import EpollSelector

import numpy as np
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
import pickle
import os
import datetime
# from multiprocessing import Process, Queue
from simulator.models import Client, Simulation
from utils.logs import get_logger
import logging

class SimulatorBase:
    def __init__(self, name=None, group_name=None, get_logger=None, 
        item=None, id=None, **kwargs):

        self.name = name
        self.group_name = group_name
        self.get_logger = get_logger
        if self.get_logger is None:
            self.get_logger = logging.getLogger

        self.id = None
        self.dt = None
        self.history = None
        self.history_arr = None
        self.r_init = None
        self.v_init = None

        self.EPS = 1e-8
        self.record_interval = None
        
        self.start_time = None
        self.finish_time = None

        # self.client = Client()
        self.step = None

        # temporary
        self.dt2 = None
        self.last_a = None
        self.process = None

        self.load(id=id, item=item)

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

    def angular_momentum(self, r, v):
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
        if self.history_arr is None or len(self.history["rs"]) != len(self.history_arr["rs"]):
            self.history_arr = self.to_array(self.history)
        return self.history_arr

    def get_data_frames(self, **kwargs):
        if "record_interval" in kwargs:
            self.record_interval = kwargs["record_interval"]
        index = np.arange(0,len(self.history["rs"]))* self.record_interval
        dframes = dict()
        dframes["L"] = pd.DataFrame(self.get_history()["L"][:,2,:], index=index)
        for key in ['KE', 'PE', 'IE', 'BInertia']:
            dframes[key] = pd.DataFrame(self.get_history()[key], index=index)
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

        v1=np.array([0.5*np.sqrt(3),0.5,0])
        v2=np.array([0.5*np.sqrt(3),-0.5,0])
        v3=np.array([np.sqrt(1/3),0,np.sqrt(2/3)])
        
        bounds = np.sqrt(energy * 2 * self.abc**2)
        if planar:
            bounds[2] = self.EPS
        n3 = round(1+bounds[2]/v3[2])
        n1=n2=round(max(bounds[0],bounds[1])*2+1)

        def helper(x):
            return np.concatenate([-x[::-1][:-1], x])
        grid_points = [helper(np.arange(0, bnd)) for bnd in np.array([n1,n2,n3])/sigma_grid]
        integer_points = np.stack(np.meshgrid(*grid_points)).reshape(3,-1)
        points = sigma_grid * np.array([v1,v2,v3]).T.dot(integer_points)
        
    #     r_init = points
        r_init = points[:, self.external_potential(points) < energy]

        shift_eps=max(0,(sigma_grid-self.sigma)*0.5*position_random_shift_percentage)
        r_init += np.random.uniform(-shift_eps,shift_eps, r_init.shape)
        self.r_init = r_init
        return r_init

    def L_given_E_constraint(self,energy):
        N = self.particle_number()
        
        P0 = (self.external_potential_energy(self.r_init, None).sum() 
            + 0.5*self.interaction_energy(self.r_init, None).sum())
        E1 = N * energy - P0
        I0 = self.moment_of_inertia_z(self.r_init,None).sum()
        return np.sqrt(2*I0*E1), E1

    def init_velocities(self, energy, angular_momentum, **kwargs):
        self.v_init = np.random.randn(*self.r_init.shape)

        E0 = self.kinetic_energy(None, self.v_init).sum()
        I0 = self.moment_of_inertia_z(self.r_init, None).sum()
        L0 = self.angular_momentum(self.r_init, self.v_init)[-1].sum()
        L1 = angular_momentum
        L1_max, E1 = self.L_given_E_constraint(energy)
        assert L1_max > L1

        alpha1 = -(np.sqrt(2*E1*I0 - L1**2)/np.sqrt(2*E0*I0 - L0**2))
        omega1 = ((-2*E1*I0*L0 + L0*L1**2 - (2*E0*I0*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2) + 
            (L0**2*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2))/(2*E1*I0**2 - I0*L1**2))
        alpha2 = np.sqrt(2*E1*I0 - L1**2)/np.sqrt(2*E0*I0 - L0**2) 
        omega2 = ((-2*E1*I0*L0 + L0*L1**2 + (2*E0*I0*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2) - 
            (L0**2*L1*np.sqrt(2*E1*I0 - L1**2))/np.sqrt(2*E0*I0 - L0**2))/(2*E1*I0**2 - I0*L1**2))
        omega2 = (-L0 + (np.sqrt(2*E0*I0 - L0**2)*L1)/np.sqrt(2*E1*I0 - L1**2))/I0
        self.v_init = alpha2 * (self.v_init + np.cross([0,0,omega2],self.r_init.T).T)
        return self.r_init, self.v_init

    def init_positions_velocities(self, energy, sigma_grid, 
        position_random_shift_percentage, planar, zero_momentum, **kwargs):
        def helper(x):
            return np.concatenate([-x[::-1][:-1], x])
        bounds = np.sqrt(energy * 2 * self.abc**2)
        if planar:
            bounds[2] = self.EPS

        grid_points = [helper(np.arange(0, bnd, sigma_grid)) for bnd in bounds]
        points = np.stack(np.meshgrid(*grid_points)).reshape(3,-1)
        points += np.random.randn(*points.shape) * position_random_shift_percentage * sigma_grid
        r_init = points[:, self.external_potential(points) < energy]
        N = r_init.shape[1]

        kinetic = (energy - self.external_potential(r_init))
        v_mag = np.sqrt(2 * kinetic)

        v_init = np.random.randn(3, N)
        if planar:
            v_init[2,:] = 0
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
            e_z = np.array([0,0,1])            
            
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
            v = v * (1-p) + p * np.array([-r[1]*omega,r[0]*omega,0])
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
    
    def before_simulation(self, r, v, t, algorithm):
        if len(self.history["rs"]) == 1:
            self.start_time = datetime.datetime.now()

    def simulate(self, iteration_time=1, dt=0.0005, record_interval=0.01, 
        algorithm="EULER", before_step=None):

        """
        r,v,a,t: initial parameters oof the system
        box: size of the box
        history: previous recordings, give if you wwant to continue simulation
        iteration_time: time to simulate
        dt: time interval of the one step
        record_interval: interval of recording the state of the system 
        """    

        logger = self.get_logger()

        self.dt = dt
        self.dt2 = dt * dt
        self.record_interval = record_interval

        if self.history is None:
            self.history = defaultdict(list)
            self.history["time"].append(0)
            self.history["rs"].append(self.r_init)
            self.history["vs"].append(self.v_init)
            for key, value in self.other_metrics(self.r_init, self.v_init, 0).items():
                    self.history[key].append(value)
        
        r = self.history["rs"][-1].copy()
        v = self.history["vs"][-1].copy()
        t = self.history["time"][-1]

        self.before_simulation(r,v,t, algorithm)
        self.update_step_function(algorithm)

        logger.info(f"starting simulation {self.name} {self.group_name}")

        for it in tqdm(range(int((iteration_time+self.EPS)/dt)), mininterval=1):
        #     r,v,a,t,dp = step_ideal(r, v,a, t)
            if before_step is not None:
                before_step(self, r, v, t)

            r,v,t = self.step(r, v, t)

            if t - self.history["time"][-1] >= record_interval - dt/4:
                self.history["time"].append(round(self.history["time"][-1]+record_interval, 6))
                self.history["vs"].append(v.copy().astype(np.float32))
                self.history["rs"].append(r.copy().astype(np.float32))
                for key, value in self.other_metrics(r,v,t).items():
                    self.history[key].append(value.astype(np.float32))
        
        self.finish_time = datetime.datetime.now()
        return self.history
    
    def simulate_async(self, iteration_time=1, dt=0.0005, record_interval=0.01, algorithm="EULER",before_step=None):
        logger = self.get_logger()
        try:
            self.simulate(iteration_time, dt, record_interval, algorithm,before_step)
        except Exception as e:
            logger.exception("exception in simulation")
            raise

        try:
            id = self.push_db()
            self.id = id
        except Exception as e:
            logger.exception("exception in pushing into db")
            raise
        logger.info(f"simulation {self.name} {self.group_name} saved by id {id}")
        return id

    def create_db_object(self):
        item = Simulation()
        item.name = self.name
        item.group_name = self.group_name
        item.start_time = self.start_time
        item.finish_time = self.finish_time
        item.L_init = self.angular_momentum(self.r_init, self.v_init)[2].sum()
        item.E_init = sum(self.system_energy(self.r_init, self.v_init)).sum()
        item.dt = self.dt
        item.particles = self.particle_number()
        item.t = self.history["time"][-1]
        item.iterations = len(self.history["time"])
        item.record_interval = self.record_interval
        item.history = self.get_history()
        return item

    def apply_item(self, item : Simulation):
        self.id = item.id
        self.name = item.name
        self.group_name = item.group_name
        self.start_time = item.start_time
        self.finish_time = item.finish_time
        
        self.history = self.to_list(item.history)
        self.dt = item.dt
        self.record_interval = item.record_interval
        self.r_init = self.history["rs"][0]
        self.v_init = self.history["vs"][0]
        
        
    def push_db(self):
        item = self.create_db_object()
        # self.id = self.client.push(item)
        self.id = Client().push(item)
        return self.id
        
    def load(self, item : Simulation = None, id = None):
        try:            
            if item is not None:
                self.apply_item(item)
            elif id is not None:
                client = Client()
                item = client.query_simulation(id)
                self.apply_item(item)
            elif self.id is not None:
                client = Client()
                item = client.query_simulation(self.id)
                self.apply_item(item)
        except Exception as e:
            logger = self.get_logger()
            logger.exception("Exception in loading item from db")
            raise

        return self