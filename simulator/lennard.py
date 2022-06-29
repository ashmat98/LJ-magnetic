import numpy as np
from collections import defaultdict
from tqdm import tqdm
from simulator.ideal import SimulatorIdeal

class SimulatorLennard(SimulatorIdeal):
    def __init__(self, sigma, epsilon, **kwargs):
        super().__init__(**kwargs)
        self.sigma = sigma
        self.epsilon = epsilon
        
        self.last_a = None

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

    # def LJ_force_2(diff, params):
    #     """
    #     r: NxNx3 ndarray
    #     r[i,j]: distance vector from j to i, 
    #             i.e. r_i - r_j
    #     return F
    #     F[i,j] = force on i by j
    #     F[i,i] = 0
    #     """
    #     dist = norm(diff)
        
    #     one_over_r_power6 = (dist) ** (-6)
    #     one_over_r_power12 = one_over_r_power6 ** 2
        
    #     comon_part = 4 * (12 * one_over_r_power12 - 
    #                                 6 * one_over_r_power6) / dist**2
    #     F = comon_part * diff
    #     np.fill_diagonal(F[0], 0)
    #     np.fill_diagonal(F[1], 0)
    #     np.fill_diagonal(F[2], 0)
    #     return F


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
        self.LJ_potential(self, r)

    
    def calc_acceleration(self, r, v, t):
        return (np.sum(self.LJ_force(r), axis = 2) 
                + self.external_force(r)) / self.mass


