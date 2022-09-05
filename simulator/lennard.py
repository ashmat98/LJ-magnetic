from signal import Sigmasks
import numpy as np
from simulator.ideal import SimulatorIdeal
from simulator.models import Simulation

class SimulatorLennard(SimulatorIdeal):
    def __init__(self, sigma=None, epsilon=None, **kwargs):
        id, item = kwargs.pop("id", None), kwargs.pop("item", None)
        super().__init__(**kwargs)
        self.sigma = sigma
        self.epsilon = epsilon
        
        self.load(id=id, item=item)

    def LJ_potential(self, r):
        r = r * (1 / self.sigma)

        diff = self.calc_diff(r, with_nan=True)
        dist = self.norm(diff)
        

        one_over_r_power6 = 1/((dist) ** (6))
        one_over_r_power12 = one_over_r_power6 ** 2
        
        potential = self.epsilon * (one_over_r_power12 - one_over_r_power6)
        
        np.fill_diagonal(potential, 0)
        return potential

    def LJ_potential_derivative(self, r):
        r = r * (1 / self.sigma)
        
        diff = self.calc_diff(r, with_nan=True)
        dist = self.norm(diff)
        
        one_over_r_power6 = (dist) ** (-6)
        one_over_r_power12 = one_over_r_power6 ** 2
        
        derivative = -  (12 * one_over_r_power12 - 
                        6 * one_over_r_power6) / dist
        np.fill_diagonal(derivative, 0)

        return self.epsilon * derivative * (1/self.sigma)

    def LJ_force(self, r):
        """
        r: NxNx3 ndarray
        r[i,j]: distance vector from j to i, 
                i.e. r_i - r_j
        return F
        F[i,j] = force on i by j
        F[i,i] = 0
        """
        r = r * (1/self.sigma)

        diff = self.calc_diff(r, with_nan=True)
        dist = self.norm(diff)
        self.last_r_dist = dist

        one_over_r_power6 = (dist) ** (-6)
        one_over_r_power12 = one_over_r_power6 ** 2
        
        comon_part =  (12 * one_over_r_power12 - 
                                    6 * one_over_r_power6) / dist**2
        F = comon_part * diff
        np.fill_diagonal(F[0], 0)
        np.fill_diagonal(F[1], 0)
        np.fill_diagonal(F[2], 0)
        return  self.epsilon * F * (1/self.sigma)
    
    def interaction_energy(self, r, v):
        return np.sum(self.LJ_potential(r), axis=1)

    
    def calc_acceleration(self, r, v, t):
        return (np.sum(self.LJ_force(r), axis = 2) 
                + self.external_force(r))

    def other_metrics(self, r, v, t):
        return {"KE": self.kinetic_energy(r,v), 
                "PE": self.external_potential_energy(r,v),
                "IE": self.interaction_energy(r,v),
                "L" : self.angular_momentum(r, v),
                "OMEGA": self.angular_velocity(r, v),
                "collisions": self.collision_count
        }

    def dump_dict(self):
        data = super().dump_dict()
        data.update({
            "sigma" : self.sigma,
            "epsilon" : self.epsilon
            })
        return data
    
    def create_db_object(self):
        item : Simulation = super().create_db_object()
        item.sigma = self.sigma
        item.epsilon = self.epsilon
        return item

    def apply_item(self, item: Simulation):
        super().apply_item(item)
        self.sigma = item.sigma
        self.epsilon = item.epsilon
        
    def volume_fraction(self, E=None):
        if E is None:
            E = self.total_energy(self.r_init, self.v_init)
        N = self.particle_number()

        r = self.sigma/2
        particle_vol = 4*np.pi*r**3/3
        potential_unit_volume = np.pi * np.prod(self.abc) * (2*E/N)**1.5
        return (N * particle_vol) / potential_unit_volume

    def collision_update(self, r):
        dist = self.last_r_dist
        # diff = self.calc_diff(r, with_nan=True)
        # dist = self.norm(diff)
        # dist = self.calc_dist(r)
        coll = (dist < 1.122).astype(int)
        # print(np.sum(coll))
        self.collision_count += np.sum((self.collision_state ^ coll) & self.collision_state)
        self.collision_state = coll
        # print(self.last_r_dist)
        # 1 -> 0  1
        # 1 -> 1  0
        # 0 -> 1  0
        # 0 -> 0  0        
        
