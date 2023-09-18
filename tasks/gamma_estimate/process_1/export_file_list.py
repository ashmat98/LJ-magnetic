import os
import sys
from tqdm import tqdm
import adddeps

files = []


def case1():
    from simulator.models import Client, Simulation

    client = Client()
    files = []

    with client.Session() as session:
        query = (session.query(Simulation.hash)
                 .where(Simulation.group_name.in_(["GE 2.2"] ))
                 ).all()
    

    for file, in query:
        file += ".hdf5"
        files.append(file + "\n")

    with open("tasks/gamma_estimate/process_1/paths.txt", "w") as f:
        f.writelines(files)

    print(f"Total {len(files)} files")

if __name__=="__main__":
    case1()