import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
import numpy as np
from simulator import SimulatorMagnetic
from tqdm import tqdm


# finer version of GE 2.0

P0=202.60790384216835; I0=292.4312; N=343

params_model = {
    "group_name" : "GE 2.2",
    "R" : 1.0,
    "Rz" : 0.25,
    "Bz" : 0,
    "eccentricity": 0.0,
    "sigma":0.1,
    "epsilon":0.1,
}
params_init = {
    "energy_for_position_init":1,
    # "energy": 1,
    "sigma_grid":0.23,
    "position_random_shift_percentage": 0.0/100,
    # "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    # "iteration_time" : 1,
    "iteration_time" : 10000,
    "dt" : 1e-3,
    "record_interval" : 5e-2,
    "algorithm" : "VERLET",
    # "before_step" : "tasks.gamma_estimate.run_jobs GE1_0.before_step"
}

if __name__ == "__main__":
    omegas = np.linspace(0,0.95,200)
    temps = np.linspace(0.03, 0.6, 200)

    i=0
    for o in tqdm(omegas):
        for t in temps:
            
            params_init["angular_momentum"] = N * t * 2 * o / (1-o**2)
            params_init["energy"] = t * (3 - o**2) / (1 - o**2)
            

            if params_init["energy"]<P0/N + 0.001:
                continue
            E1 = N * params_init["energy"] - P0        
            if params_init["angular_momentum"] > np.sqrt(2*I0*E1):
                continue
            
            sim = SimulatorMagnetic(**params_model)
            sim.init_positions_closepack(**params_init)
            # print(sim.external_potential_energy(sim.r_init, None).sum())
            print(np.sum(sim.r_init[:2]**2))
            Lmax, _ = sim.L_given_E_constraint(params_init["energy"])
            # print(Lmax)
            # assert Lmax > params_init["angular_momentum"]




            # continue
            # submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=1, 
            #     job_name=f"{params_model['group_name']}",
            #     print_summary=False, time_factor=1.7, memory_factor=2, success_email=False)
            
            i+=1
            

    # submit_all_jobs(as_array=True)



            # sim = SimulatorMagnetic(**params_model)
            # sim.init_positions_closepack(**params_init)
            
            # def boo(self, energy):
            #     N = self.particle_number()
            #     P0 = (self.external_potential_energy(self.r_init, None).sum() 
            #         + 0.5*self.interaction_energy(self.r_init, None).sum())
            #     E1 = N * energy - P0
            #     I0 = self.moment_of_inertia_z(self.r_init,None).sum()

            #     print(P0,I0,N)
            # boo(sim, params_init["energy"])


            




