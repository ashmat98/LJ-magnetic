
import adddeps
import numpy as np

e0=1
l0=0.6
a0=1

T = e0 * (1 - a0**2 * l0**2 / e0**2)/( (1 + 3 * a0**2 * l0**2 / e0**2)**0.5 + 2 )
Om = e0 / l0 * ( (1 + 3 * a0**2 * l0**2 / e0**2)**0.5 - 1 )

def get_el(T, Om, a, N):
    e =  T * (3 * a**2 - Om**2 )/ (a**2-Om**2)
    l =  T * (2 * Om )/ (a**2-Om**2)
    return e, l

from simulator import SimulatorMagnetic

def generate_data(a, T, Om):
    e, l = get_el(T, Om, a, 33*a**3)
    
    params_model = {
        "group_name" : "Ensemble 6",
        "R" : a * 1.0,
        "Rz" : a * 0.25,
        "Bz" : 0,
        "eccentricity": 0.00,
        "sigma":0.1,
        "epsilon":0.1,
#         "get_logger" : get_logger
    }
    params_init = {
        "energy": 1,
        "sigma_grid":0.5,
        "position_random_shift_percentage": 50.0/100,
        # "angular_momentum_factor" : 0.6,
        "angular_momentum" : 60,
        "planar": False,
        "zero_momentum": False,
    }
    
    sim = SimulatorMagnetic(**params_model)
    sim.init_positions_closepack(**params_init)
    N = sim.particle_number()
    e, l = get_el(T, Om, a, 33*a**3)
    params_init["energy"] = e
    params_init["angular_momentum"] = l * N
    
    params_simulation = {
        "iteration_time" : 20,
        "dt" : 1e-4,
        "record_interval" : 1e-1,
        "algorithm" : "VERLET"
    }



    sim = SimulatorMagnetic(**params_model)
    sim.init_positions_closepack(**params_init)
    return sim.simulate_estimate(**params_simulation), params_model, params_init, params_simulation


# In[12]:


f(1, T, Om)[0]


# In[40]:


x = np.linspace(0.5**3,5**3, 1000)**(1/3)
y = [f(x1, T, Om) for x1 in x]
plt.scatter(x, y)
plt.plot(x, 33 * x**(3), c="r")


# In[28]:


set([f(x, T, Om) for x in np.linspace(0.5,3, 1000)])


# In[ ]:



