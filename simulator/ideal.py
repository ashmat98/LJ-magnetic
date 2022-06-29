from cv2 import Algorithm
import numpy as np
from collections import defaultdict
from tqdm import tqdm
from simulator.base import SimulatorBase

class SimulatorIdeal(SimulatorBase):
    def __init__(self, abc, mass, **kwargs):
        super().__init__(**kwargs)
        self.mass = mass
        self.abc = abc
        self.abc_inv_square = self.abc ** (-2)
        
        self.step = None
        self.last_a = None

    def external_potential(self, r):
        r_sq = np.power(r,2)
        return 0.5 * np.dot(self.abc_inv_square,r_sq)

    def external_force(self, r):
        return - r * self.abc_inv_square[:, None]

    def calc_acceleration(self, r, v, t):
        return self.external_force(r) / self.mass

    def external_potential_energy(self, r, v):
        return self.external_potential(r)

    def interaction_energy(self, r, v):
        return 0

    def other_metrics(self, r, v, t):
        return {"KE": self.kinetic_energy(r,v), 
                "PE": self.external_potential_energy(r,v)
        }
