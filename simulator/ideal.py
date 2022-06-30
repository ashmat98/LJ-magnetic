import numpy as np
from simulator.base import SimulatorBase

class SimulatorIdeal(SimulatorBase):
    def __init__(self, abc=None, mass=None, **kwargs):
        super().__init__(**kwargs)
        self.mass = mass
        self.abc = abc
        self.initialize()

    def initialize(self):
        if self.abc is not None:
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
        return np.zeros(r.shape[1])

    def other_metrics(self, r, v, t):
        return {"KE": self.kinetic_energy(r,v), 
                "PE": self.external_potential_energy(r,v)
        }

    def dump_dict(self):
        data = super().dump_dict()
        data.update(
            {"abc" : self.abc,
             "mass" : self.mass}
        )
        return data

    def apply_loaded(self, data):
        super().apply_loaded(data)
        self.abc = data["abc"]
        self.mass = data["mass"]
        self.initialize()
