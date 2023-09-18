import pandas as pd
import numpy as np
from simulator.lennard import SimulatorLennard
from simulator.hdf5IO import Simulation

class SimulatorRotating(SimulatorLennard):
    def __init__(self, phi, omega, **kwargs):
        __load = kwargs.pop("__load", True)
        super().__init__(__load=False, **kwargs)
        
        self.phi = phi
        self.omega = omega     

        if __load:
            self.load(**kwargs)

    def external_potential(self, r):
        t = self._simulation_t
        phi = self.phi + self.omega * t
        c, s = np.cos(phi), np.sin(phi)
        R = np.array(((c, s, 0), (-s, c,0),(0,0,1)))
        
        r_sq = np.power(R.dot(r),2)
        return 0.5 * np.dot(self.abc_inv_square,r_sq)

    def external_force(self, r):
        t = self._simulation_t

        phi = self.phi + self.omega * t
        c, s = np.cos(phi), np.sin(phi)
        R = np.array(((c, s, 0), (-s, c,0),(0,0,1)))
        R_inv = np.array(((c, -s, 0), (s, c,0),(0,0,1)))

        return - R_inv.dot(R.dot(r) * self.abc_inv_square[:, None])


    def other_metrics(self, r, v, t):
        metrics = super().other_metrics(r,v,t)

        if self._placeholder_LJ_force is None:
            self.calc_acceleration(r, v, t)

        metrics.update({
            "phi": np.array(self.phi + self.omega * t, dtype="float32")
        })
        return metrics
    
    def get_data_frames(self, **kwargs):
        dframes = super().get_data_frames(**kwargs)

        index = dframes["index"]
        
        for key in ['phi']:
            dframes[key] = pd.DataFrame(self.get_history()[key], index=index)
            
        return dframes

    def create_item(self):
        item : Simulation = super().create_item()
        return item

    def apply_item(self, item: Simulation):
        super().apply_item(item)

        
