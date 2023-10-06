import h5py
import numpy as np

def convert_particle_prop_to_total_prop(hdf5_path):
    
    history = dict()
    with h5py.File(hdf5_path, 'r') as f:
        for key in f:
            history[key] = np.array(f[key])
        particles = f.attrs.get("particles")
    
    
    ts = history["time"].round(5)
    rs = history["rs"].transpose(1,0,2)
    vs = history["vs"].transpose(1,0,2)
    
    prefix = "total/"
    # self.history.push(prefix+"Iz", np.sum(r[0]**2 + r[1]**2, axis=-1))

    history[prefix+"xx"] = np.mean(rs[0]**2,axis=-1)
    history[prefix+"yy"] = np.mean(rs[1]**2,axis=-1)
    history[prefix+"zz"] = np.mean(rs[2]**2,axis=-1)
    history[prefix+"xy"] = np.mean(rs[0]*rs[1],axis=-1)

    history[prefix+"vxvx"] = np.mean(vs[0]**2,axis=-1)
    history[prefix+"vyvy"] = np.mean(vs[1]**2,axis=-1)
    history[prefix+"vzvz"] = np.mean(vs[2]**2,axis=-1)
    history[prefix+"vxvy"] = np.mean(vs[0]*vs[1],axis=-1)


    omega_MLE = np.mean(rs[0]* vs[1]-rs[1]* vs[0], axis=1) / np.mean(rs[0]**2+rs[1]**2, axis=-1)

    beta_MLE = (1/3 * np.mean( (vs[0]+omega_MLE[:,None] * rs[1])**2 + (vs[1]-omega_MLE[:,None] * rs[0])**2 + (vs[2])**2,axis=-1))**-1

    history[prefix+"omega_MLE"] = omega_MLE
    history[prefix+"beta_MLE"] = beta_MLE

    history[prefix+"L"] = history["L"][:,2].sum(axis=-1)
    history[prefix+"E"] = np.sum(0.5 * history["IE"] + history["PE"] + history["KE"], axis=-1)
    history[prefix+"KE"] = np.sum(history["KE"], axis=-1)
    history[prefix+"PE"] = np.sum(history["PE"], axis=-1)
    history[prefix+"IE"] = np.sum(history["IE"], axis=-1)


    if "collisions" in history:
        for i, c in enumerate(history["collisions"].T):
            history[prefix+f"collisions-{i+1}"] = c

    return {key:value for key, value in history.items() if "total/" in key}