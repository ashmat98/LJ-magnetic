import os


HDF5_PATH = "../hdf5s/"
LOG_PATH = "../logs/"
RESULT_PATH = "../results"

if os.getenv("HOSTNAME") in ["newton", "vesta", "z2-26"]:
    HDF5_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "hdf5s")
    LOG_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "logs")
    RESULT_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "results")
    

HDF5_PATH = os.getenv("HDF5_PATH", HDF5_PATH)
LOG_PATH = os.getenv("LOG_PATH", LOG_PATH)
LOG_FILE = os.getenv("LOG_FILE", "simulation.log")
