# import adddeps
import os
import argparse
import shutil

import h5py

HDF5_PATH = os.getenv("HDF5_PATH")

def clean_fields(hash):
    path = os.path.join(HDF5_PATH, hash+".hdf5")
    with h5py.File(path, "a") as ds:
        if "_repack1" in ds.attrs():
            return
        for key in ds.keys():
            if key not in ["total", "vs", "rs", "time"]:
                del ds[key]
                # print("del", key)
    os.system(f"h5repack \"{path}\" \"{path}.hdf5\"")
    os.remove(path)
    os.rename(path+".hdf5", path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--hash", type=str)
    args = parser.parse_args()

    path = os.path.join(HDF5_PATH, args.hash+".hdf5")
    local = "./" + args.hash + ".hdf5"

    with h5py.File(path, "a") as ds:
        if "_repack1" in ds.attrs.keys():
            exit(0)

    shutil.copy(path, "./")
    os.system(f"h5repack \"{local}\" \"{local}.hdf5\"")

    with h5py.File(local+".hdf5", "a") as ds:
        ds.attrs["_repack1"] = True
    
    shutil.move(local+".hdf5", path)


    

