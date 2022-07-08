import numpy as np
from simulator.lennard import SimulatorLennard
from simulator.models import Simulation

class SimulatorMagnetic(SimulatorLennard):
    def __init__(self, Bz=None, **kwargs):
        id, item = kwargs.pop("id", None), kwargs.pop("item", None)
        super().__init__(**kwargs)
        self.Bz = Bz
        self.load(id=id, item=item)

    
    def calc_acceleration(self, r, v, t):
        return (np.sum(self.LJ_force(r), axis = 2) 
                + self.external_force(r)) 

    def step_VERLET(self, r, v, t):
        """
        Verlet algorithm with magnetic field
        """
        dt, dt2 = self.dt, self.dt2  # dt2 is dt^2
        a = self.last_a
        omega = self.Bz 

        r1 = (r + v * dt + 0.5 * a * dt2 
            + 0.5 * dt2 * omega * np.cross(v[:2].T,[0,0,1]).T)
        a1 = self.calc_acceleration(r1, np.nan, np.nan)
        v1 = v + 0.5 * (a + a1) * dt

        inv_denom = 1 / (1 + 0.25 * omega**2 * dt2)
        v1[0, :] = (v1[0] + dt * omega * v[1] 
            + 0.25 * dt2 * omega * (a[1] + a1[1] - omega * v[0])) * inv_denom

        v1[1, :] = (v1[1] - dt * omega * v[0] 
            - 0.25 * dt2 * omega * (a[0] + a1[0] + omega * v[1])) * inv_denom

        self.last_a = a1

        return r1, v1, self.next_time(t)

    def other_metrics(self, r, v, t):
        metrics = super().other_metrics(r, v, t)
        metrics["BInertia"] = 0.5 * self.Bz * np.sum(r[:2]**2, axis=0)
        return metrics

    def apply_loaded(self, data):
        super().apply_loaded(data)
        self.Bz = data["Bz"]
    
    def create_db_object(self):
        item : Simulation = super().create_db_object()
        item.Bz = self.Bz
        return item

    def apply_item(self, item: Simulation):
        super().apply_item(item)
        self.Bz = item.Bz