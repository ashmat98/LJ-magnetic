import datetime
import h5py
import os
import numpy as np
from settings import HDF5_PATH, DFS_PATH
import pandas as pd

class Simulation:
    def __init__(self) -> None:
        self.id = None
        self.name = None
        self.group_name = None
        self.cls = None
        self.start_time = None
        self.finish_time = None
        self.eccentricity = None
        self.a = None
        self.b = None
        self.c = None
        self.epsilon = None
        self.sigma = None
        self.particles = None
        self.Bz = None
        self.L_init = None
        self.E_init = None
        self.other = None
        self.dt = None
        self.record_interval = None
        self.t = None
        self.iterations = None
        self.hash = None
        self.history = None
        self.history_essential = None


    def load_history(self, keys=None):
        self.history = Client_HDF5.load_history(
            os.path.join(HDF5_PATH, self.hash + ".hdf5"), keys=keys)
            
    def load_df(self, path=None):
        self.df = pd.read_hdf(os.path.join(DFS_PATH, self.hash + ".hdf5"))
        return self.df
    
    def get_hdf5_object(self):
        hdf5_path = os.path.join(DFS_PATH, self.hash + ".hdf5")
        return h5py.File(hdf5_path, 'r')
    
    def get_member_variables(self):
        member_variables = [attr for attr in dir(self) 
                            if not callable(getattr(self, attr)) and 
                            not attr.startswith("_")]
        return member_variables



class Client_HDF5:
    def __init__(self, path):
        self.path = path

    def push(self, item : Simulation):
        
        with h5py.File(self.path, 'w') as f:
            def set_value(key, value):
                if value is not None:
                    f.attrs[key] = value

            set_value("id", item.id)
            set_value("name", item.name)
            set_value("group_name", item.group_name)
            set_value("start_time", item.start_time.timestamp())
            set_value("finish_time", item.finish_time.timestamp())
            set_value("eccentricity", item.eccentricity)
            set_value("a", item.a)
            set_value("b", item.b)
            set_value("c", item.c)
            set_value("epsilon", item.epsilon)
            set_value("sigma", item.sigma)
            set_value("particles", item.particles)
            set_value("Bz", item.Bz)
            set_value("L_init", item.L_init)
            set_value("E_init", item.E_init)
            set_value("other", item.other)
            set_value("dt", item.dt)
            set_value("record_interval", item.record_interval)
            set_value("t", item.t)
            set_value("iterations", item.iterations)
            set_value("hash", item.hash)

            for key, value in item.history.items():
                f.create_dataset(key, data=value)

    @staticmethod
    def load_history(hdf5_path, keys=None):
        with h5py.File(hdf5_path, 'r') as f:
            history = dict()
            for key in f:
                if keys is not None and key not in keys:
                    continue
                history[key] = np.array(f[key])
        return history

    def load(self, full_load=True):
        item = Simulation()
        with h5py.File(self.path, 'r') as f:
            item.id = f.attrs.get("id")
            item.name = f.attrs.get("name")
            item.group_name = f.attrs.get("group_name")
            item.eccentricity = f.attrs.get("eccentricity")
            item.a = f.attrs.get("a")
            item.b = f.attrs.get("b")
            item.c = f.attrs.get("c")
            item.epsilon = f.attrs.get("epsilon")
            item.sigma = f.attrs.get("sigma")
            item.particles = f.attrs.get("particles")
            item.Bz = f.attrs.get("Bz")
            item.L_init = f.attrs.get("L_init")
            item.E_init = f.attrs.get("E_init")
            item.other = f.attrs.get("other")
            item.dt = f.attrs.get("dt")
            item.record_interval = f.attrs.get("record_interval")
            item.t = f.attrs.get("t")
            item.iterations = f.attrs.get("iterations")
            item.hash = f.attrs.get("hash")

            item.start_time = datetime.datetime.fromtimestamp(
                f.attrs.get("start_time"))
            item.finish_time = datetime.datetime.fromtimestamp(
                f.attrs.get("finish_time"))

        if full_load:
            item.history = self.load_history(self.path)

        return item