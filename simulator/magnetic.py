import numpy as np
from simulator.lennard import SimulatorLennard
from simulator.models import Simulation

class SimulatorMagnetic(SimulatorLennard):
    def __init__(self, Bz=None, **kwargs):
        load = kwargs.pop("load", False)
        super().__init__(load=False, **kwargs)
        self.Bz = Bz

        if load:
            self.load(**kwargs)

    
    def calc_acceleration(self, r, v, t):
        return (np.sum(self.LJ_force(r), axis = 2) 
                + self.external_force(r)) 

    def step_VERLET(self, r, v, t):
        """
        Verlet algorithm with magnetic field
        """
        if self.last_a is None:
            self.last_a = self.calc_acceleration(r, v, t)

        dt, dt2 = self.dt, self.dt2  # dt2 is dt^2
        a = self.last_a
        omega = self.Bz 

        r1 = (r + v * dt + 0.5 * a * dt2 )
            # + 0.5 * dt2 * omega * np.cross(v[:2].T,[0,0,1]).T)
        r1[0, :] += 0.5 * dt2 * omega * v[1,:]
        r1[1, :] -= 0.5 * dt2 * omega * v[0,:]
        
        a1 = self.calc_acceleration(r1, np.nan, np.nan)
        v1 = v + 0.5 * (a + a1) * dt

        inv_denom = 1 / (1 + 0.25 * omega**2 * dt2)
        v1[0, :] = (v1[0] + dt * omega * v[1] 
            + 0.25 * dt2 * omega * (a[1] + a1[1] - omega * v[0])) * inv_denom

        v1[1, :] = (v1[1] - dt * omega * v[0] 
            - 0.25 * dt2 * omega * (a[0] + a1[0] + omega * v[1])) * inv_denom

        self.last_a = a1

        return r1, v1, self.next_time(t)

    def step_VERLET_new(self, r, v, t):
        """
        Verlet algorithm with magnetic field
        """
        if self.last_a is None:
            self.last_a = self.calc_acceleration(r, v, t)

        dt, dt2 = self.dt, self.dt2  # dt2 is dt^2
        a = self.last_a
        omega = self.Bz 

        r += (v * dt + 0.5 * a * dt2 
            + 0.5 * dt2 * omega * np.cross(v[:2].T,[0,0,1]).T)
        a1 = self.calc_acceleration(r, np.nan, np.nan)
        a += a1
        v1 = v + 0.5 * (a) * dt

        inv_denom = 1 / (1 + 0.25 * omega**2 * dt2)
        
        v1[0, :] += (dt * omega * v[1] 
            + 0.25 * dt2 * omega * (a[1] - omega * v[0]))
        v1[1, :] += ( - dt * omega * v[0] 
            - 0.25 * dt2 * omega * (a[0] + omega * v[1]))

        v1[:2, :] *= inv_denom
        self.last_a[:] = a1
        
        return r, v1, self.next_time(t)

    def other_metrics(self, r, v, t):
        metrics = super().other_metrics(r, v, t)
        metrics["BInertia"] = 0.5 * self.Bz * np.sum(r[:2]**2, axis=0)
        return metrics

    def apply_loaded(self, data):
        super().apply_loaded(data)
        self.Bz = data["Bz"]
    
    def create_item(self):
        item : Simulation = super().create_item()
        item.Bz = self.Bz
        return item

    def apply_item(self, item: Simulation):
        super().apply_item(item)
        self.Bz = item.Bz