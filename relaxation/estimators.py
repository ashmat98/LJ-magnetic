
import pandas as pd
import scipy as sp
from scipy.special import legendre
from scipy.integrate import simpson
import numpy as np
from simulator.base import SimulatorBase
from tqdm import tqdm

EPS = 1e-6
class RelaxationFinder:
    def __init__(self, sim: SimulatorBase, tmax=None, step=2,verbose=True) -> None:
        self.verbose = verbose
        self.step=step
        self.sim = sim
        self.dfs = sim.get_data_frames()
        self.tmax = tmax
        if self.tmax is None:
            self.tmax = max(self.dfs["index"])

        self.collision = self.collision_method()
        self.precalc()
        self.cossim,_ = self.cossim_method()
        self.rmsd = self.rmsd_method()
        self.rmsv = self.rmsv_method()

    def summarize(self, stdout=False):
        summary = dict()
        summary.update(
            dict(zip(["col-1","col-1.06", "col-1.12"],self.collision))
        )
        summary.update(
            dict(zip(["csim-3","csim-4", "csim-9", "csim-m"],
            [self.cossim[3],self.cossim[4],self.cossim[9],np.median(self.cossim[3:])]))
        )
        summary.update({
            "rmsd":self.rmsd,
            "rmsv":self.rmsv
            })
        if stdout:
           for key, value in summary.items():
             print(f"{key+':':10} {value:0.3f}")

        return summary

    def collision_method(self):
        sim = self.sim
        cols = self.dfs["collisions"]
        return sim.particle_number()/(EPS+np.polyfit(cols.index, cols.values, 1)[0])

    def precalc(self):
        sim = self.sim
        ts = sim.get_history()["time"]
        vs = sim.get_history()["vs"]
        rs = sim.get_history()["rs"]
        us=(vs/np.sqrt(np.sum(vs**2,axis=1, keepdims=True))).transpose(0,2,1)

        arr_cossim = []
        arr_rmsd = []
        arr_rmsv = []
        ind = []
        for d in tqdm(range(1,np.argmax(ts>=self.tmax),self.step), 
                disable=not self.verbose):
            ind.append(ts[d])

            cossim = np.matmul(us[d:,:,None,:],us[:-d,:,:,None])[:,:,0,0]
            arr_cossim.append([])
            for n in range(1,10):
                val = np.mean(legendre(n)(cossim),axis=0)
                arr_cossim[-1].append(val)
            
            rmsd=(np.sqrt(np.mean(np.sum(np.square(rs[d:]-rs[:-d]),axis=1),axis=1)))
            arr_rmsd.append(np.mean(rmsd))
            
            rmsv=(np.sqrt(np.mean(np.sum(np.square(vs[d:]-vs[:-d]),axis=1),axis=1)))
            arr_rmsv.append(np.mean(rmsv))

        self.arr_cossim = np.array(arr_cossim)
        self.arr_rmsd = np.array(arr_rmsd)
        self.arr_rmsv = np.array(arr_rmsv)
        self.ind = np.array(ind)

    def cossim_method(self):
        df = pd.DataFrame(self.arr_cossim.mean(axis=2), 
            index=self.ind, columns=range(1,self.arr_cossim.shape[1]+1))
        vals = np.array([0]+[simpson(df[i], df.index) for i in df.columns])
        vals_abs = np.array([1]+[simpson(abs(df[i]), df.index) for i in df.columns])

        return vals, vals_abs

    def rmsd_method(self):
        return self.ind[np.argmax(self.arr_rmsd > np.median(self.arr_rmsd))]
    def rmsv_method(self):
        return self.ind[np.argmax(self.arr_rmsv > np.median(self.arr_rmsv))]
        