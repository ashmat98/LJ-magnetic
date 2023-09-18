#!/usr/bin/env python

import adddeps
import argparse
import os
import shutil

from simulator.hdf5IO import Client_HDF5, Simulation
from simulator.models import Client, SimulationAlchemy as Sim
from settings import HDF5_PATH, RESULT_PATH
from tqdm import tqdm


def clean_unlinked_items(act=True):
    client = Client()
    ids_to_remove = []
    with client.Session() as sess:
        for sid, _hash in sess.query(Sim.id, Sim.hash):    
            if not os.path.exists(os.path.join(HDF5_PATH, _hash+".hdf5")):
                ids_to_remove.append(sid)
    if len(ids_to_remove) > 0:
        if act:
            client.remove_simulation(ids_to_remove)
            print(f"{len(ids_to_remove)} unlinked simulation entries sucsessfully deleted!")
        else:
            print(f"{len(ids_to_remove)} unlinked simulation entries found.")
    else:
        print("Database is completely linked.")

def clean_unlinked_files(act=True):
    client = Client()
    removed = 0
    with client.Session() as sess:
        for file in tqdm(os.listdir(HDF5_PATH)):
            path = os.path.join(HDF5_PATH, file)
            _hash, ext = os.path.splitext(file)
            assert ext == ".hdf5"
        
            c = sess.query(Sim.id).where(Sim.hash==_hash).count()
            if c ==0:
                if act:
                    os.remove(path)
                removed += 1
    if removed > 0:
        print(f"{removed} unlinked hdf5 files " + ("sucsessfully deleted!" if act else "detected"))
    else:
        print("All files are linked.")

def add_unlinked_files(act=True, delete_failed=False):
    client = Client()
    added = 0
    with client.Session() as sess:
        all_hash = sess.query(Sim.hash).all()
        all_hash = set([h for h, in all_hash])
        print("All hashes loaded from db.")
        for file in tqdm(os.listdir(HDF5_PATH)):
            path = os.path.join(HDF5_PATH, file)
            _hash, ext = os.path.splitext(file)
            assert ext == ".hdf5"
        
            # c = sess.query(Sim.id).where(Sim.hash==_hash).count()
            c = 1 if _hash in all_hash else 0
            if c ==0:
                if act:
                    try:
                        item = Client_HDF5(path).load(full_load=False)
                        Client().push(item)
                        
                    except Exception as e:
                        print(e)
                        print()
                        added -=1
                        if delete_failed:
                            os.remove(path)
                            print(f"Corrupted {file} is deleted.")
                        else:
                            print(f"{file} is corrupted. ")
                            print("   ", str(e))
                added += 1
                
    if added > 0:
        print(f"{added} unlinked hdf5 files " + ("sucsessfully added!" if act else "can be added."))
    else:
        print("All files are linked.")
    



def add_results_to_db(path, clean_after=True, act=True, delete_failed=False):
    added = 0
    jobs = os.listdir(path)
    for job in tqdm(jobs):
        for file in os.listdir(os.path.join(path, job)):
            if os.path.splitext(file)[1] == ".hdf5":
                hdf5_from = os.path.join(path,job,file)
                hdf5_to = os.path.join(HDF5_PATH,file)

                if os.path.exists(hdf5_to):
                    print(f"job {job} already exists")
                    continue

                if act is False:
                    added += 1
                    continue
                try:
                    if clean_after:
                        os.rename(hdf5_from, hdf5_to)
                        item = Client_HDF5(hdf5_to).load(full_load=False)

                        Client().push(item)
                        shutil.rmtree(os.path.join(path, job))
                    else:
                        item = Client_HDF5(hdf5_from).load(full_load=True)
                        Client().push(item)
                    added += 1

                except OSError as e:
                    if os.path.exists(hdf5_to):
                        os.rename(hdf5_to, hdf5_from)
                    if delete_failed:
                        shutil.rmtree(os.path.join(path, job))
                        print(f"Corrupted job {job} is deleted")
                    else:
                        print(f"Job {job} is corrupted.")
                        print(f"  full path: {os.path.join(path, job)}")
                        print("   ", str(e))

                

                
    print(f"{added} items " + ("can be " if not act else "") + "added to database.")
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--act", action="store_true")
    parser.add_argument("--delete-failed", action="store_true")
    parser.add_argument("--delete", action="store_true", dest="delete_failed")

    parser.add_argument("--clean-unlinked-items", action='store_true', help="Delete items from database which are not linked to a hd5f file")
    parser.add_argument("--clean-unlinked-files", action='store_true', help="delete hdf5 files which are not registered in database.")
    parser.add_argument("--add-unlinked-files", action='store_true', help="register hdf5 files to database")
    parser.add_argument('--move-results', help="move hdf5 filed from the results folder to the hdf5s' filder and register to the database",
                        const=RESULT_PATH,
                        default=None,
                        action='store',
                        nargs='?',
                        type=str)

    parser.add_argument("--copy-results", default=None, type=str)


    args = parser.parse_args()

    if args.clean_unlinked_items:
        clean_unlinked_items(args.act)
    if args.clean_unlinked_files:
        clean_unlinked_files(args.act)
    
    if args.add_unlinked_files:
        add_unlinked_files(args.act, args.delete_failed)

    if args.move_results is not None:
        add_results_to_db(args.move_results, clean_after=True, 
            act=args.act, delete_failed=args.delete_failed)
    
    if args.copy_results is not None:
        add_results_to_db(args.copy_results, clean_after=False, 
            act=args.act, delete_failed=args.delete_failed)
    
    if args.act is False:
        print("\n  Use argument --act to make changes")