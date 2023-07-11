import datetime
from datetime import timedelta
import subprocess
from simulator import SimulatorMagnetic
import json
import os

partitions = [
    (timedelta(minutes=10),"debug"),
    (timedelta(hours=2), "short"),
    (timedelta(days=2), "medium"),
    (timedelta(days=14), "long"),
    (timedelta(days=28), "extra_long")
 ]

submitted_jobs = []

def submit_with_estimates_and_params(params_model, params_init, params_simulation, 
                                     script="scripts/general_job.sh", job_name="", copies=1, print_only=False, 
                                     success_email=False,
                                     time_factor=1, memory_factor=1):
    sim = SimulatorMagnetic(**params_model)
    sim.init_positions_closepack(**params_init)

    estimate = sim.simulate_estimate(**params_simulation)

    time_estimate = estimate["time"] * 1.5  # + 50%
    time_estimate = datetime.timedelta(
            seconds=int(time_factor * time_estimate.total_seconds()))    
    days = time_estimate.days
    rest = time_estimate - datetime.timedelta(days=days)
    time_estimate_str = f"{days}-{rest}"

    memory_estimate = 2000 + int(memory_factor * estimate["memory"] * 1.3) # + 30%
    
    
    
    for (time_limit, partition) in partitions:
        if time_estimate < time_limit:
            break
    else:
        raise Exception(f"Very long calculation requested, Estimated time {time_estimate_str}")

    print(f"""
       Job name:   {job_name}
Particle number:   {sim.particle_number()}
 Estimated time:   {time_estimate},
         memory:   {memory_estimate:0.1f}MB
      partition:   {partition}
         copies:   {copies}
        """)
    
    output_path = f'/home/ashmat/cluster/outputs/{job_name}_{params_model["group_name"].replace(" ", "_")}'
    os.makedirs(output_path, exist_ok=True)
    output_path += "/%A_%a.out"
    
    # print(time_estimate_str)
    # return
    my_env = os.environ.copy()
    my_env.update({
        "PARAMS_MODEL": json.dumps(params_model),
        "PARAMS_INIT": json.dumps(params_init),
        "PARAMS_SIMULATION": json.dumps(params_simulation)
    })

    args = [
        "sbatch",
        f"--time={time_estimate_str}",
        f"--mem-per-cpu={memory_estimate}",
        f"--partition={partition}",
        f"--job-name={job_name}",
        f"--array=0-{copies-1}",
        f"--output={output_path}"]
    if success_email:
        args.append("--mail-type=END")

    args.append(script)

    submitted_jobs.append(
        {"args": args,
        "env": my_env}
    )

    # subprocess.run([
    #     ".venv/bin/python",
    #     "scripts/run_simulation_with_params.py"
    # ], env={
    #     "PARAMS_MODEL": json.dumps(params_model),
    #     "PARAMS_INIT": json.dumps(params_init),
    #     "PARAMS_SIMULATION": json.dumps(params_simulation)
    # })
    
def submit_all_jobs(ask_confirmation=True):
    if ask_confirmation:
        reply = input(f"Submit {len(submitted_jobs)} jobs? [y/N]")
        if reply == "y":
            for kwargs in submitted_jobs:
                subprocess.run(**kwargs)