#!/usr/bin/env python3
import adddeps
from simulator.models import Client
import argparse
import os, time
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--group-name", type=str, required=True)
    parser.add_argument("--shift", type=int, required=True)
    parser.add_argument("--wide", type=int, required=True)
    parser.add_argument("--dt1", type=int, required=True)
    parser.add_argument("--dt2", type=int, required=True)
    parser.add_argument("--W", type=int, nargs="+")

    args = parser.parse_args()

    client = Client()
    items = client.get_simulation_groups([args.group_name])

    file_path = os.path.join(os.getenv("TMPDIR"), str(time.time())+".txt")

    with open(file_path, "w") as f:
        for item in items:
            f.write(
                "--hash={} --shift={} --wide={} --dt1={} --dt2={} ".format(
                    item.hash, args.shift, args.wide, args.dt1, args.dt2)
                    )
            if args.W is not None:
                f.write("--W " + " ".join(map(str, args.W)))
            f.write("\n")
    
    print("param file:", file_path)

    my_env = os.environ.copy()

    my_env.update({"PARAM_FILE":file_path})
        
    command_args = [
        "sbatch",
        f"--array=1-{len(items)}",
        # f"--array=1-1",
        "scripts/precalc_acs/job_script.sh"
    ]

    print(" ".join(command_args))
    
    subprocess.run(args=command_args, env=my_env)
