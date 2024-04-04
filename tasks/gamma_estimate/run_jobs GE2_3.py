import adddeps
from utils.submit_job import submit_with_estimates_and_params, submit_all_jobs
import numpy as np
from simulator import SimulatorMagnetic
from tqdm import tqdm


# finer version of GE 2.0

# P0=202.60790384216835; I0=292.4312; N=523
P0 = None; I0=None; N=None

params_model = {
    "group_name" : "GE 2.3",
    "cls":"SimulatorLennardLammps",
    "R" : 1.0,
    "Rz" : 0.25,
    "eccentricity": 0.0,
    "sigma":0.05,
    "epsilon":0.1,
}
params_init = {
    "energy_for_position_init":1,
    # "energy": 1,
    "sigma_grid":1,
    "position_random_shift_percentage": 0.0/100,
    # "angular_momentum_factor" : 0.95,
    # "angular_momentum" : 0,
    "planar": False,
    "zero_momentum": False,
}
params_simulation = {
    "iteration_time" : 50000,
    "dt" : 1e-3,
    "record_interval" : 5e-1,
    "output_particles" : 150,
    "particle_properties":True,
    "total_properties": True
}

scale = 5
params_model["R"] *= scale
params_model["Rz"] *= scale

if __name__ == "__main__":
    omegas = np.linspace(0,0.95,50)
    temps = np.linspace(0.03, 0.6, 50)

    i=0
    for o in tqdm(omegas):
        for t in temps:
            if N is None:
                sim = SimulatorMagnetic(**params_model)
                sim.init_positions_closepack(energy=0,**params_init)
                N = sim.particle_number()
                
                P0 = (sim.external_potential_energy(sim.r_init, None).sum() 
                     + 0.5*sim.interaction_energy(sim.r_init, None).sum())
                
                I0 = np.sum(sim.r_init[:2]**2)
                print({"I0":I0,"N":N,"P0":P0})

            params_init["angular_momentum"] = N * t * 2 * o / (1-o**2)
            params_init["energy"] = t * (3 - o**2) / (1 - o**2)
            

            if params_init["energy"]<P0/N + 0.001:
                continue
            E1 = N * params_init["energy"] - P0        
            if params_init["angular_momentum"] > np.sqrt(2*I0*E1):
                continue
            
            # sim = SimulatorMagnetic(**params_model)
            # sim.init_positions_closepack(**params_init)
            # Lmax, _ = sim.L_given_E_constraint(params_init["energy"])
            # assert Lmax > params_init["angular_momentum"]

            submit_with_estimates_and_params(params_model, params_init, params_simulation,copies=1, 
                job_name=f"{params_model['group_name']}",
                print_summary=False, time_factor=1., memory_factor=2, success_email=False)
            
            i+=1
            

    submit_all_jobs(as_array=True)



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


            




