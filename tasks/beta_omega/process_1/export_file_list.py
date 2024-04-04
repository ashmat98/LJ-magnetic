import os
import shutil
import sys
from tqdm import tqdm
import adddeps
from simulator.models import Client, SimulationAlchemy

files = []


def case1():

    client = Client()
    files = []

    with client.Session() as session:
        query = (session.query(SimulationAlchemy.hash)
                 .where(SimulationAlchemy.group_name.in_(["BO 3.lammps"] ))
                 ).all()
    

    for file, in query:
        file += ".hdf5"
        files.append(file + "\n")

    output_path = os.path.join(os.getenv("DATA"), "tmp", "beta_omega__process_1__paths.txt")

    with open(output_path, "w") as f:
        f.writelines(files)

    print("path:" , output_path)

    # copy sript as well
    output_path = os.path.join(os.getenv("DATA"), "tmp", "beta_omega__process_1__script.py")
    shutil.copy("tasks/beta_omega/process_1/script.py", output_path)
    print("path:" , output_path)


    print(f"Total {len(files)} files")

    print(f"run: \nsbatch --array=1-{len(files)} tasks/beta_omega/process_1/job_script.sh")


if __name__=="__main__":
    case1()