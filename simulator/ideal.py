import numpy as np
from simulator.baseIO import SimulatorBaseIO
from simulator.models import Simulation
import pandas as pd

class SimulatorIdeal(SimulatorBaseIO):
    def __init__(self, R=None, Rz=None, eccentricity=None, abc=None, **kwargs):
        __load = kwargs.pop("__load", True)
        
        super().__init__(__load=False, **kwargs)
        
        self.R = R
        self.Rz = Rz
        self.eccentricity = eccentricity
        self.abc = abc

        self.init_potential_params()
        if __load:
            self.load(**kwargs)

    def init_potential_params(self):
        if self.abc is not None:
            self.Rz = self.abc[2]
            self.R = (0.5*self.abc[1]**2 + 0.5*self.abc[0]**2)**0.5
            if (self.abc[1]/self.abc[0])<1:
                self.eccentricity = np.sqrt(1-(self.abc[1]/self.abc[0])**2)
        elif self.eccentricity is not None and self.R is not None:
            self.abc =  np.array(
                    [self.R / (1-self.eccentricity**2)**(1/4),
                    self.R * (1-self.eccentricity**2)**(1/4),
                    self.Rz]
                )
        
        if self.abc is not None:
            self.abc_inv_square = self.abc ** (-2)
        

    def external_potential(self, r):
        r_sq = np.power(r,2)
        return 0.5 * np.dot(self.abc_inv_square,r_sq)

    def external_force(self, r):
        return - r * self.abc_inv_square[:, None]

    def calc_acceleration(self, r, v, t):
        return self.external_force(r)

    def external_potential_energy(self, r, v):
        return self.external_potential(r)

    def interaction_energy(self, r, v):
        return np.zeros(r.shape[1])

    def other_metrics(self, r, v, t):
        return {"KE": self.kinetic_energy(r,v), 
                "PE": self.external_potential_energy(r,v)
        }

    def get_data_frames(self, **kwargs):
        dframes = super().get_data_frames(**kwargs)
        for key in ['KE', 'PE']:
            dframes[key] = pd.DataFrame(self.get_history()[key], index=dframes["index"])
        return dframes

    def apply_item(self, item: Simulation):
        super().apply_item(item)
        self.abc = np.array([item.a, item.b, item.c])
        self.init_potential_params()
        
    def create_item(self):
        item : Simulation = super().create_item()
        item.eccentricity = self.eccentricity
        item.a, item.b, item.c = self.abc
        return item