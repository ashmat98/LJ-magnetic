import os

SOURCE_PATH = "/home/ashmat/cluster/LJ-magnetic"

HDF5_PATH = "../hdf5s/"
DFS_PATH = "../dfs/"
LOG_PATH = "../logs/"
RESULT_PATH = "../results"

if (os.getenv("HOSTNAME") in ["newton", "vesta", "z2-26"] 
        and os.getenv("DATA") is not None):
    HDF5_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "hdf5s")
    DFS_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "dfs")
    LOG_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "logs")
    RESULT_PATH = os.path.join(os.getenv("DATA"),"LJ-magnetic", "results")
    

HDF5_PATH = os.getenv("HDF5_PATH", HDF5_PATH)
DFS_PATH = os.getenv("DFS_PATH", DFS_PATH)
LOG_PATH = os.getenv("LOG_PATH", LOG_PATH)
LOG_FILE = os.getenv("LOG_FILE", "simulation.log")
