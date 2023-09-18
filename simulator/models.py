import os

import json
import h5py
import numpy as np
import pandas as pd
import datetime

from settings import HDF5_PATH, DFS_PATH
from simulator.hdf5IO import Simulation, Client_HDF5

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

class SimulationAlchemy(Base):
    __tablename__ = "simulation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    group_name = Column(Text)
    cls = Column(Text)
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
    
    @staticmethod
    def convert_from(item: Simulation):
        new_item = SimulationAlchemy()

        members = item.get_member_variables()
        for attr in members:
            setattr(new_item, attr, getattr(item, attr))
        return new_item
    
    def convert(self) -> Simulation:
        item = Simulation()
        members = item.get_member_variables()
        for attr in members:
            setattr(item, attr, getattr(self, attr))
        return item

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

    def push(self, item : Simulation):
        item = SimulationAlchemy.convert_from(item)

        output_path = os.path.join(HDF5_PATH, f"{item.hash}.hdf5")
        if not os.path.exists(output_path):
            Client_HDF5(output_path).push(item)
        item.history = None
        
        with self.Session() as sess:
            sess.add(item)
            sess.commit()
            sess.refresh(item)
            
        return item.id

    def query_last_simulation(self, full_load=True) -> Simulation:
        with self.Session() as sess:
            item : SimulationAlchemy = sess.query(SimulationAlchemy).order_by(
                SimulationAlchemy.start_time.desc()).first()
        item = item.convert()
        if full_load:
            item.load_history()

        return item

    def query_simulation(self, id=-1, full_load=True) -> Simulation:
       
        with self.Session() as sess:
            item : SimulationAlchemy = (sess.query(SimulationAlchemy)
                .where(SimulationAlchemy.id>=id)
                .order_by(SimulationAlchemy.id).first())
        
        item = item.convert()

        if full_load:
            item.load_history()

        return item
    
    def remove_simulation(self, id):
        with self.Session() as sess:
            if type(id) is int:
                sql = delete(SimulationAlchemy).where(SimulationAlchemy.id==id)
            else:
                sql = delete(SimulationAlchemy).where(SimulationAlchemy.id.in_(id))
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
