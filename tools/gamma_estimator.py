import numpy as np
import os
from simulator.hdf5IO import Simulation
from settings import HDF5_PATH, ACS_PATH
import scipy.optimize
from utils.ACfunctions import Cr, Cv, AC
from tqdm.notebook import tqdm
import pandas as pd
import h5py


class Engine:
    def __init__(self, item, shift, wide):
        self.item = item
        
        self.dt = item.record_interval
        self.times = np.arange(0, item.t+0.1*self.dt, self.dt).round(5)

        self.a = 0.5*(1/item.a+1/item.b)
        self.eps = 0.5*(1/item.a-1/item.b) / self.a
        
        self.shift = shift
        self.wide = wide
        self.time_points = None

        self.vc = None

        self.data = None

    def load_df(self):
        self.item.load_df()
        self.df = self.item.df

    def load_vc(self):
        if self.item.history is None or "vs" not in self.item.history:
            self.item.load_history(["vs"])
        vs = self.item.history["vs"]
        self.vc = vs[:,0] + 1j * vs[:,1]
    
    def delete_vc(self):
        del self.vc
        self.item.history.pop("vs")
        self.vc = None

    def generate_time_points(self, dt1, dt2):
        item, shift, wide = self.item, self.shift, self.wide

        tfinal = self.times[-1]
      
        beta = np.log(dt2/dt1)/(tfinal-shift)

        time_points = [1.1 * wide]
        tlast = time_points[-1]
        delta_t = dt1
        for t in self.times:
            if t > tlast+delta_t and t < tfinal-wide:
                tlast = t
                time_points.append(t)
                if t > shift:
                    delta_t = dt1* np.exp(beta*(t-shift))
        
        time_points = np.array(time_points[:-1])
        # time_points = time_points[time_points>0.8*shift]

        self.time_points = time_points

        self.data = [{"t":t} for t in time_points]

        return time_points
    
    def _get_range(self, t, wide=None):
        if wide is None:
            wide = self.wide + 1e-6
        l = np.searchsorted(self.times, t - wide/2)
        r = np.searchsorted(self.times, t + wide/2)
        return l, r
    
    def get_ac(self, t):
        
        l, r = self._get_range(t)
        
        vc = self.vc[l:r+1]
        
        ac = [AC(vc[:,k]) for k in range(vc.shape[-1])]
        ac = np.stack(ac, axis=-1)
        
        return ac.mean(axis=-1)
    
    def calc_acs(self, progress=False):
        self.acs = np.array([self.get_ac(t) for t in 
                             tqdm(self.time_points, disable=not progress)])
    
        self.ac_time = self.dt * np.arange(self.acs.shape[1])
    
    @property
    def _hdf_path(self):
        return os.path.join(ACS_PATH, self.item.hash + ".hdf5")
    
    def dump(self):
        with h5py.File(self._hdf_path, "w") as ds:
            ds["acs"] = self.acs
            ds.attrs["shift"] = self.shift
            ds.attrs["wide"] = self.wide
            ds["time_points"] = self.time_points
            
            
            frame = pd.DataFrame(self.data)
            for key in frame:
                ds[f"frame/{key}"] = frame[key].values

    def load(self, acs=True):
        if not os.path.exists(self._hdf_path):
            return False
        with h5py.File(self._hdf_path, "r") as ds:
            if acs is True:
                self.acs = ds["acs"][:]
                self.ac_time = self.dt * np.arange(self.acs.shape[1])

            self.time_points = ds["time_points"][:]
            
            if self.shift != ds.attrs["shift"]:
                print("shift=", ds.attrs["shift"])
                raise Exception("shift does not match")
            if self.wide != ds.attrs["wide"]:
                print("wide=", ds.attrs["wide"])
                raise Exception("wide does not match")
            
            ds_frame = ds["frame"]
            self.data = [dict() for _ in self.time_points]

            def add_key_to_data(key):
                for line, val in zip(self.data, ds_frame[key][:]):
                    line[key] = val

            for key in ds_frame.keys():
                if isinstance(ds_frame[key], h5py.Dataset):
                    add_key_to_data(key)
                else:
                    for key2 in ds_frame[key].keys():
                        add_key_to_data(f"{key}/{key2}")

                

    
        
    def calc_rest(self):
        df = self.df

        for line in self.data:
            t = line["t"]
            l, r = self._get_range(t)
            subdf = df.iloc[l:r+1]
            line["T"] = (subdf["beta_MLE"].values**-1).mean()
            line["O"] = subdf["omega_MLE"].values.mean()
            line["L"] = subdf["L"].values.mean()
            
    def gamma_1(self, ac, line, W):
        ts = self.ac_time
        T, O, a = line["T"], line["O"], self.a
        def f(gamma):
            c = Cv(ts[:W], gamma, T, O, a)
            c1 = ac[:W]
            d = c-c1
            return np.real(d.dot(d.conj())) / len(d)
        
        optres = scipy.optimize.minimize(f, 1,bounds=[(0.0001, 10)])

        return {"crit1": optres.fun, "g1": optres.x[0]}
    
    def gamma_2(self, ac, line, W):
        ts = self.ac_time

        T, O, a = line["T"], line["O"], self.a

        def f(gamma):
            c = Cv(ts[:W], gamma, T, O, a)
            c1 = ac[:W]
            c = c * (c1[0]/c[0])
            d = c-c1
            return np.real(d.dot(d.conj())) / len(d)
        
        optres = scipy.optimize.minimize(f, 1,bounds=[(0.0001, 10)])

        return {"crit2": optres.fun, "g2": optres.x[0]}
    
    @staticmethod
    def _get_ratio(ts, g, r):
        def f(t, g, r):
            return np.exp(-0.5 * g * t * (1+r))/(1+r)**2 + np.exp(-0.5 * g * t * (1-r))/(1-r)**2

        lac = np.log(f(ts, g, r))
        slope, _ = np.polyfit(ts, lac, 1)
        return slope/g

    @staticmethod
    def _moving_average(a, n=3):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def _get_lac(self, ac):
        period = int(2 * np.pi / self.a / self.dt)
        ts = self._moving_average(self.ac_time, period)
        ac = self._moving_average(np.abs(ac), period)
        lac = np.log(ac)

        return ts, lac

    def gamma_3(self, ac, line, W, iterations=3):
        a = self.a
        
        r = line["O"] / a

        ts, lac = self._get_lac(ac)
        
        slope,_ = np.polyfit(ts[:W], lac[:W], 1)
        
        gamma = 0.01
        for _ in range(iterations):
            ratio = self._get_ratio(ts, gamma, r)
            gamma = slope / ratio
            
        return {"g3":gamma}
    

    def _get_gamma(self, W, estimators=None, prefix=""):
        if estimators is None:
            estimators = [self.gamma_1, self.gamma_2, self.gamma_3]

        W_points = int(W/self.dt)
        updates = [dict() for ac in self.acs]

        for ac, line, update in zip(self.acs, self.data, updates):
            for estimator in estimators:
                for key, val in estimator(ac, line, W_points).items():
                    update[prefix+key] = val
        return updates
    
    def _apply_data(self, updates):
        for line, update in zip(self.data, updates):
            line.update(update)
        

    def calc_gamma(self, W, estimators=None, prefix=""):
        self._apply_data(
            self._get_gamma(W, estimators, prefix)
        )
    

    
