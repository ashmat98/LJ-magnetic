from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData, engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import relationship,sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text, PickleType, JSON )
from sqlalchemy.sql.expression import text
import json

Base = declarative_base()
CONNECTION_STRING_SQLITE = "sqlite:///simulations.db"
CONNECTION_STRING = 'postgresql://localhost:5432/lj_simulations'
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
    history = Column(PickleType)



class Client:
    def __init__(self, disk=False) -> None:
        if disk:
            self.engine = create_engine(CONNECTION_STRING_SQLITE, poolclass=NullPool)    
        else:
            self.engine = create_engine(CONNECTION_STRING, poolclass=NullPool)
        self.Session = sessionmaker(bind=self.engine)
        create_table(self.engine)

    def push(self, item : Simulation):
        with self.Session() as sess:
            sess.add(item)
            sess.commit()
            sess.refresh(item)
        return item.id
        
    def query_last_simulation(self):
        with self.Session() as sess:
            item : Simulation = sess.query(Simulation).order_by(Simulation.start_time.desc()).first()


    def query_simulation(self, id=-1):
       
        with self.Session() as sess:
            item : Simulation = (sess.query(Simulation)
                .where(Simulation.id>=id)
                .order_by(Simulation.id).first())

        return item
        

        
                