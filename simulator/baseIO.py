
import hashlib
import os
from simulator.models import Client, Client_HDF5, Simulation
from simulator.settings import HDF5_PATH
from utils.logs import get_logger
import logging
from simulator.base import SimulatorBase
import time
import numpy as np


class SimulatorBaseIO(SimulatorBase):
    def __init__(self, name=None, group_name=None, get_logger=None, 
        item = None, id=None, only_essential=None, hdf5_path=None, **kwargs):
        __load = kwargs.pop("__load", True)

        super().__init__(**kwargs)
        self.name = name
        self.group_name = group_name
        self.get_logger = get_logger
        if self.get_logger is None:
            self.get_logger = logging.getLogger

        self.id = None
        self.process = None
        
        self.only_essential = only_essential

        if __load:
            self.load(**kwargs)


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

    def create_item(self):
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
        
        if self.only_essential is None:
            item.history = self.get_history()
        else:
            item.history_essential = self.only_essential(self)

        item.hash = self.hash()

        self.collision_init()
        return item

    def apply_item(self, item : Simulation):
        self.id = item.id
        self.name = item.name
        self.group_name = item.group_name
        self.start_time = item.start_time
        self.finish_time = item.finish_time
        self.dt = item.dt
        self.record_interval = item.record_interval
        
        self.history = item.history
        

        #TODO: merge history and essential history
        if self.history is not None:
            # self.history = self.to_list(self.history)

            self.r_init = self.history["rs"][0]
            self.v_init = self.history["vs"][0]

        if item.history_essential is not None:
            self.history_essential = item.history_essential
        
        self.collision_init()

        
    def hash(self):
        #TODO: use essentia. hostory too!
        hashable = (self.id, self.name, self.group_name, os.getpid(),
            self.start_time, self.finish_time, str(self.history["rs"]))
        hashable_str = tuple(str(x) for x in hashable)
        return hashlib.md5("".join(hashable_str).encode()).hexdigest()[::2]
        
    def push_hdf5(self):
        item = self.create_item()
        output_path = os.path.join(HDF5_PATH, f"{item.hash}.hdf5")
        Client_HDF5(output_path).push(item)
        return output_path

    def push_db(self):
        item = self.create_item()
        # self.id = self.client.push(item)
        self.id = Client().push(item)
        return self.id
        
    def load(self, item : Simulation = None, id = None, hdf5_path=None, **kwargs):
        try:    
            if item is not None:
                self.apply_item(item)
            elif id is not None:
                item = Client().query_simulation(id, full_load=True)
                self.apply_item(item)
            elif hdf5_path is not None:
                item = Client_HDF5(hdf5_path).load()
                self.apply_item(item)
            elif self.id is not None:
                item = Client().query_simulation(self.id, full_load=True)
                self.apply_item(item)

        except Exception as e:
            logger = self.get_logger()
            logger.exception("Exception in loading item from db")
            raise

        return self