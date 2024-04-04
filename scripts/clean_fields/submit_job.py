#!/usr/bin/env python3
import adddeps
from simulator.models import Client
import argparse
import os, time
import subprocess

import adddeps
import argparse
import os
import shutil

from simulator.hdf5IO import Client_HDF5, Simulation
from simulator.models import Client, SimulationAlchemy as Sim
from settings import HDF5_PATH, RESULT_PATH
from tqdm import tqdm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parser.add_argument("--group-name", type=str, required=True)

    args = parser.parse_args()

    group_names = ["ER 3.303.35.lammps",
        "ER 3.303.55.lammps",
        "ER 3.303.45.lammps",
        "ER 3.303.6.lammps",
        "ER 3.303.15.lammps",
        "ER 3.303.25.lammps"]
    
    client = Client()
    with client.Session() as sess:
        hashs = sess.query(Sim.hash).where(Sim.group_name.in_(group_names)).all()

    print(len(hashs))
    

    file_path = os.path.join(os.getenv("TMPDIR"), str(time.time())+".txt")

    with open(file_path, "w") as f:
        for hash, in tqdm(hashs[::]):
            f.write(hash + "\n")
    
    print("param file:", file_path)

    my_env = os.environ.copy()

    my_env.update({"PARAM_FILE":file_path})
        
    command_args = [
        "sbatch",
        f"--array=1-{len(hashs)}",
        # f"--array=1-1",
        "scripts/clean_fields/job_script.sh"
    ]

    print(" ".join(command_args))
    
    subprocess.run(args=command_args, env=my_env)
