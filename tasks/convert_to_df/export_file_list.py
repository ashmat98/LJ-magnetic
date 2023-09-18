import os
import sys
from tqdm import tqdm
import adddeps

files = []

def case1():
    # all files that are not processed
    dfs_files = os.listdir(os.getenv("dfs_dir"))

    for file in tqdm(os.listdir(os.getenv("hdf5_dir"))):
        filepath = os.path.join(os.getenv("hdf5_dir"), file)
        
        if file not in dfs_files:
            size_GB = os.path.getsize(filepath)/1024**3
            if size_GB < 100:
                files.append(file + "\n")

    with open("file_names.txt", "w") as f:
        f.writelines(files)

    print(f"Total {len(files)} files")

def case2():
    from simulator.models import Client, Simulation

    client = Client()
    # reprocess specific entries
    hdf5_files = os.listdir(os.getenv("hdf5_dir"))

    files = []

    with client.Session() as session:
        query = (session.query(Simulation.hash)
                #  .where(Simulation.group_name.in_(["ER 6.2"] ))
                 ).all()
    

    for file, in query:
        file += ".hdf5"
        if file not in hdf5_files:
            continue

        filepath = os.path.join(os.getenv("hdf5_dir"), file)
       
        files.append(file + "\n")

    with open("file_names.txt", "w") as f:
        f.writelines(files)

    print(f"Total {len(files)} files")

if __name__=="__main__":
    case1()