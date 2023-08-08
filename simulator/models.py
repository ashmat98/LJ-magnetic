import os

import json
import h5py
import numpy as np
import pandas as pd
import datetime

from settings import HDF5_PATH, DFS_PATH

from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData, engine, delete
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import relationship, sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text, PickleType, JSON )
from sqlalchemy.sql.expression import text
from psycopg2.extensions import register_adapter, AsIs

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(np.float64, addapt_numpy_float64)
register_adapter(np.int64, addapt_numpy_int64)



Base = declarative_base()
CONNECTION_STRING_SQLITE = "sqlite:///simulations.db"
CONNECTION_STRING = 'postgresql://localhost:54320/lj_simulations'
# CONNECTION_STRING = 'postgresql:///lj_simulations'

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(CONNECTION_STRING, poolclass=NullPool)


def create_table(engine):
    Base.metadata.create_all(engine)

class Simulation(Base):
    __tablename__ = "simulation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    group_name = Column(Text)
    start_time = Column(DateTime)
    finish_time = Column(DateTime)
    eccentricity = Column(Float)
    a = Column(Float)
    b = Column(Float)
    c = Column(Float)
    epsilon = Column(Float)
    sigma = Column(Float)
    particles = Column(Integer)
    Bz = Column(Float)
    L_init = Column(Float)
    E_init = Column(Float)
    other = Column(JSON)
    dt = Column(Float)
    record_interval = Column(Float)
    t = Column(Float)
    iterations = Column(Integer)
    hash = Column(Text)
    history = Column(PickleType, nullable=True)
    history_essential = Column(PickleType, nullable=True)

    def load_history(self, keys=None):
        if "hdf5" in self.history:
            self.history = Client_HDF5.load_history(
                os.path.join(HDF5_PATH, self.history["hdf5"]), keys=keys)
            
    def load_df(self, path=None):
        if "hdf5" in self.history:
            self.df = pd.read_hdf(os.path.join(DFS_PATH, self.history["hdf5"]))
            return self.df
        else:
            raise NotImplementedError

    def get_hdf5_object(self):
        hdf5_path = os.path.join(DFS_PATH, self.history["hdf5"])
        return h5py.File(hdf5_path, 'r')
    
    # def delete_dfs(names):
    #     for name in names:

    
class Client:
    def __init__(self, disk=False) -> None:
        if disk:
            self.engine = create_engine(CONNECTION_STRING_SQLITE, poolclass=NullPool)    
        else:
            self.engine = create_engine(CONNECTION_STRING, poolclass=NullPool)
        self.Session = sessionmaker(bind=self.engine)
        create_table(self.engine)

    def push(self, item : Simulation, link_hdf5=True):
        if link_hdf5:
            output_path = os.path.join(HDF5_PATH, f"{item.hash}.hdf5")
            if not os.path.exists(output_path):
                Client_HDF5(output_path).push(item)
            item.history = {"hdf5" : item.hash + ".hdf5"}
        
        with self.Session() as sess:
            sess.add(item)
            sess.commit()
            sess.refresh(item)
            
        return item.id

    def query_last_simulation(self, full_load=True):
        with self.Session() as sess:
            item : Simulation = sess.query(Simulation).order_by(Simulation.start_time.desc()).first()
        
        if full_load:
            item.load_history()

        return item

    def query_simulation(self, id=-1, full_load=True):
       
        with self.Session() as sess:
            item : Simulation = (sess.query(Simulation)
                .where(Simulation.id>=id)
                .order_by(Simulation.id).first())
        
        if full_load:
            item.load_history()

        return item
    
    def remove_simulation(self, id):
        with self.Session() as sess:
            if type(id) is int:
                sql = delete(Simulation).where(Simulation.id==id)
            else:
                sql = delete(Simulation).where(Simulation.id.in_(id))
            sess.execute(sql)
            sess.commit()
            

        
"""
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
        """
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