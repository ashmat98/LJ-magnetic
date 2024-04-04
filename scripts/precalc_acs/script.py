# import adddeps
import os, sys
from tools.gamma_estimator import Engine
from settings import HDF5_PATH
from simulator.hdf5IO import Client_HDF5, Simulation
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--hash", type=str)
    parser.add_argument("--shift", type=int)
    parser.add_argument("--wide", type=int)
    parser.add_argument("--dt1", type=int)
    parser.add_argument("--dt2", type=int)
    parser.add_argument("--W", type=int, nargs="+")

    args = parser.parse_args()



    item = Client_HDF5(hash=args.hash).load(full_load=False)
    print("group_name:",item.group_name)
    print("step 1")
    engine = Engine(item, args.shift, args.wide)
    print("step 2")

    engine.load_vc()
    print("step 3")

    engine.generate_time_points(args.dt1, args.dt2)
    print("time points:", len(engine.time_points))
    engine.calc_acs()   
    engine.load_df()
    engine.calc_rest() 
    if args.W is not None:
        for W in args.W:
            engine.calc_gamma(W, prefix=f"{W}/")

    engine.dump()


