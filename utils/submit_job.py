import datetime
from datetime import timedelta
import subprocess
from simulator import SimulatorMagnetic
import json
import os
from tqdm import tqdm
import time
import numpy as np

from utils.utils import get_simulation_class

MaxArraySize = 10000

partitions = [
    (timedelta(minutes=10),"debug"),
    (timedelta(hours=2), "short"),
    (timedelta(days=2), "medium"),
    (timedelta(days=14), "long"),
    (timedelta(days=28), "extra_long")
 ]
def get_partition(time_estimate):
    for (time_limit, partition) in partitions:
        if time_estimate < time_limit:
            break
    else:
        raise Exception(f"Very long calculation requested, Estimated time {get_time_estimate_str(time_estimate)}")
    return partition

def get_time_estimate_str(time_estimate):
    days = time_estimate.days
    rest = time_estimate - datetime.timedelta(days=days)
    time_estimate_str = f"{days}-{rest}"
    
    return time_estimate_str

submitted_jobs = []

def submit_with_estimates_and_params(params_model, params_init, params_simulation, 
                                     script="scripts/general_job.sh", job_name="", copies=1, print_summary=True, 
                                     success_email=False,
                                     time_estimate=None,
                                     time_factor=1.5, memory_factor=1.3, sbatch_args=list(), **kwargs):
    if "print_only" in kwargs:
        print("WARNING: Do not use print_only argument.")
    
    sim_class_name = params_model.get("cls", "SimulatorMagnetic")
    SimulatorClass = get_simulation_class(sim_class_name)

    sim = SimulatorClass(**params_model)
    sim.init_positions_closepack(**params_init)

    estimate = sim.simulate_estimate(**params_simulation)
    
    if time_estimate is None:
        time_estimate = estimate["time"]
    elif type(time_estimate) in (int, float):
        time_estimate =  datetime.timedelta(
            seconds=int(time_estimate)) 

    time_estimate = datetime.timedelta(
            seconds=int(time_factor * time_estimate.total_seconds()))    
    

    memory_estimate = 2000 + int(memory_factor * estimate["memory"] ) # + 30%
    
    
    partition = get_partition(time_estimate)
    
    
    # output_path = f'/home/ashmat/cluster/outputs/{job_name}_{params_model["group_name"].replace(" ", "_")}'
    # os.makedirs(output_path, exist_ok=True)
    # output_path += "/%A_%a.out"
    


    # print(time_estimate_str)
    # return
    # my_env = os.environ.copy()
    my_env = {}

    if "Lammps" in sim_class_name:
        my_env["USE_LAMMPS"] = "true"
        params_simulation["run_lammps"] = True
        memory_estimate += 10000
        time_estimate += datetime.timedelta(minutes=25)
    
    my_env.update({
        "PARAMS_MODEL": json.dumps(params_model),
        "PARAMS_INIT": json.dumps(params_init),
        "PARAMS_SIMULATION": json.dumps(params_simulation)
    })

    args = {"time_estimate":time_estimate,
            "memory_estimate":memory_estimate,
            "partition":partition,
            "job_name":job_name,
            "copies":copies,
            "success_email":success_email,
            "script":script,
            'other_args': sbatch_args
    }
 
    submitted_jobs.append(
        {"args": args,
        "env": my_env}
    )

    if print_summary:
        print(f"""
        Job name:   {job_name}
    Particle number:   {sim.particle_number()}
    Estimated time:   {time_estimate},
            memory:   {memory_estimate:0.1f}MB
        partition:   {partition}
            copies:   {copies}
            """)


    
def submit_all_jobs(ask_confirmation=True, as_array=False):
    global submitted_jobs
    
    if ask_confirmation:
        reply = input(f"Submit {len(submitted_jobs)} jobs? [y/N]")
        if reply == "y":
            if not as_array:
                _submit_separate_jobs()
            else:
                _submit_as_array()


def _submit_separate_jobs():
    my_env = os.environ.copy()

    for job in submitted_jobs:
        args = job["args"]
        my_env.update(job["env"])
        
        time_estimate_str = get_time_estimate_str(args["time_estimate"])
        
        command_args = [
            "sbatch",
            f"--time={time_estimate_str}",
            f"--mem-per-cpu={args['memory_estimate']}",
            f"--partition={args['partition']}",
            f"--job-name={args['job_name']}",
            f"--array=0-{args['copies']-1}",
            # f"--output={output_path}"
        ]
        command_args += args["other_args"]

        if args['success_email']:
            command_args.append("--mail-type=END")
        command_args.append(args["script"])

        subprocess.run(args=command_args, env=my_env)

def _submit_as_array():
    time_estimate = datetime.timedelta(seconds=0) 
    memory_estimate = 0
    success_email = False
    script = None

    lines = []
    my_env = os.environ.copy()

    for job in tqdm(submitted_jobs):
        args = job["args"]
        params = job["env"]

        time_estimate = max(time_estimate,args["time_estimate"])
        memory_estimate = max(memory_estimate, args["memory_estimate"])
        success_email = success_email or args["success_email"]

        my_env.update(params)
        
        if script is None:
            script = args["script"]
        elif script != args["script"]:
            raise Exception("Script must be the same")
        
        copies = args["copies"]
        lines += copies * [
            f"--model='{params['PARAMS_MODEL']}' --init='{params['PARAMS_INIT']}' --simulation='{params['PARAMS_SIMULATION']}'\n"
            ]


    time_estimate_str = get_time_estimate_str(time_estimate)
    partition = get_partition(time_estimate)

    np.random.shuffle(lines)

    while len(lines) > 0:
        sublines = lines[:MaxArraySize]
        lines = lines[MaxArraySize:]

        file_path = os.path.join(my_env["TMPDIR"], str(time.time())+".txt")
        with open(file_path, "w") as f:
            f.writelines(sublines)
        
        my_env.update({"PARAM_FILE":file_path})
        
        command_args = [
            "sbatch",
            f"--time={time_estimate_str}",
            f"--mem-per-cpu={memory_estimate}",
            f"--partition={partition}",
            f"--job-name=\"{args['job_name']}\"",
            f"--array=1-{len(sublines)}",
            # f"--output={output_path}"
        ]
        if success_email:
            command_args.append("--mail-type=END")

        command_args.append(script)

        print(file_path)
        print(" ".join(command_args))
        subprocess.run(args=command_args, env=my_env)



