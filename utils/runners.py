
import numpy as np
from simulator.magnetic import SimulatorMagnetic

import os
from multiprocessing import Pool, cpu_count
from tqdm.notebook import tqdm as tqdm_notebook
from tqdm import tqdm

from utils.utils import beep, get_simulation_class

def _runner(args):
    return runner(*args) 

def multirunner(params, callback=None, processes=-1, pool=None):
    if processes == -1:
        processes = cpu_count()

    if pool is None:
        pool = Pool(processes, maxtasksperchild=1)

    new_params = []
    for i, (params_model, params_init, params_simulation) in enumerate(params):
        params_model = params_model.copy()
        params_model["verbose"] = (i==0)
        new_params.append((params_model, params_init, params_simulation, callback))
        
    res_generator = pool.imap(_runner, new_params[1:])
    res = [_runner(new_params[0])]
    res += list(tqdm(res_generator, total=len(new_params)-1))

    return res
  

def runner(params_model, params_init, params_simulation, callback=None):
    sim_class_name = params_model.pop("class", "SimulatorMagnetic")

    SimulatorClass = get_simulation_class(sim_class_name)

    params_model["name"] = params_model.get("name", os.getenv("HOSTNAME"))

    sim = SimulatorClass(**params_model)

    sim.init_positions_closepack(**params_init)
    sim.init_velocities(**params_init)
    sim.simulate(**params_simulation)

    if callback is not None:
        return callback(sim)
    
    return sim.push_hdf5()