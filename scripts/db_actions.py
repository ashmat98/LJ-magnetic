import adddeps
import argparse
import os
import shutil

from simulator.models import Client, Client_HDF5, Client, Simulation
from simulator.settings import HDF5_PATH, RESULT_PATH
from tqdm import tqdm


def clean_unlinked_items(act=True):
    client = Client()
    ids_to_remove = []
    with client.Session() as sess:
        for sid, _hash in sess.query(Simulation.id, Simulation.hash):    
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
        for file in os.listdir(HDF5_PATH):
            path = os.path.join(HDF5_PATH, file)
            _hash, ext = os.path.splitext(file)
            assert ext == ".hdf5"
        
            c = sess.query(Simulation.id).where(Simulation.hash==_hash).count()
            if c ==0:
                if act:
                    os.remove(path)
                removed += 1
    if removed > 0:
        print(f"{removed} unlinked hdf5 files " + ("sucsessfully deleted!" if act else "detected"))
    else:
        print("All files are linked.")

def add_unlinked_files(act=True):
    client = Client()
    added = 0
    with client.Session() as sess:
        for file in os.listdir(HDF5_PATH):
            path = os.path.join(HDF5_PATH, file)
            _hash, ext = os.path.splitext(file)
            assert ext == ".hdf5"
        
            c = sess.query(Simulation.id).where(Simulation.hash==_hash).count()
            if c ==0:
                if act:
                    item = Client_HDF5(path).load(full_load=False)
                    Client().push(item, link_hdf5=True)

                added += 1
    if added > 0:
        print(f"{added} unlinked hdf5 files " + ("sucsessfully added!" if act else "can be added."))
    else:
        print("All files are linked.")
    



def add_results_to_db(path, clean_after=True, act=True):
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

                if clean_after:
                    os.rename(hdf5_from, hdf5_to)
                    item = Client_HDF5(hdf5_to).load(full_load=False)

                    Client().push(item, link_hdf5=True)
                    shutil.rmtree(os.path.join(path, job))
                else:
                    item = Client_HDF5(hdf5_from).load(full_load=True)
                    Client().push(item)
                added += 1

                
    print(f"{added} items " + ("can be " if not act else "") + "added to database.")
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--act", action="store_true")
    parser.add_argument("--clean-unlinked-items", action='store_true')
    parser.add_argument("--clean-unlinked-files", action='store_true')
    parser.add_argument("--add-unlinked-files", action='store_true')
    parser.add_argument('--move-results',
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
        add_unlinked_files(args.act)

    if args.move_results is not None:
        add_results_to_db(args.move_results, clean_after=True, act=args.act)
    
    if args.copy_results is not None:
        add_results_to_db(args.copy_results, clean_after=False, act=args.act)
    
    if args.act is False:
        print("Use argument --act to make changes")