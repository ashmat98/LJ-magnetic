import os
import sys
from tqdm import tqdm
import adddeps
import h5py
from settings import HDF5_PATH
files = []

def case1():
    # all files that are not processed
    files = []
    
    for file in tqdm(os.listdir(HDF5_PATH)[:]):
        path = os.path.join(HDF5_PATH, file)
        with h5py.File(path) as f:
            if "total" in f.keys():
                continue
        
        files.append(file + "\n")

    with open("tasks/migrate_total_props/file_names.txt", "w") as f:
        f.writelines(files)

    print(f"Total {len(files)} files")

if __name__=="__main__":
    case1()