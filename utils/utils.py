import numpy as np
import importlib
import os
from settings import DFS_PATH
import pandas as pd

sounds = {
    7: 'https://github.com/ashmat98/task-finish-tools/raw/main/beep/sounds/beep-07a.wav',
    6: 'https://github.com/ashmat98/task-finish-tools/raw/main/beep/sounds/beep-06.wav',
    9: 'https://github.com/ashmat98/task-finish-tools/raw/main/beep/sounds/beep-09.wav'
}

def beep(sound=7):
    """
    beeps at run. Useful tool in jupyter notebook.
    """
    sound_file = sounds[sound]
    from IPython.display import Audio
    return Audio(sound_file, autoplay=True) 

from datetime import timedelta

def iteration_time_estimate(n):
    """
    time needed for single iteration.
    n : particle number
    """
    return timedelta(seconds=np.maximum(2e-3,  1.0e-7 * n**2.8 * 0.03))

def memory_estimate(n):
    """
    memory needed for single record in MegaBytes
    n : particle number
    """
    return (85 * n) / 1024**2

def plot_mean_std(df, color=0, label=""):
    
    from matplotlib import pyplot as plt
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    if isinstance(color, int):
        color = colors[color % len(colors)]


    m = df.mean(axis=1)
    std = df.std(axis=1)
    m.plot(color=color, label=label)
    plt.fill_between(df.index, (m + std), (m - std), color=color, alpha=0.1)


def get_function(import_path):
    import_path = import_path.split(".")
    module = importlib.import_module(".".join(import_path[:-1]))
    return getattr(module, import_path[-1])

def get_simulation_class(class_name):
    module = importlib.import_module("simulator")
    return getattr(module, class_name)


def delete_dfs(names):
    for name in names:
        file = os.path.join(DFS_PATH, name)
        if os.path.exists(file):
            os.remove(file)


def standartize(arr):
    return (arr - np.mean(arr))/np.std(arr)

def smoothen(df, time_window):
    if time_window<0:
        return df
    window = len(df.loc[0:time_window])
    df_smooth = df.rolling(window, center=True).mean()
    
    if "total_L" in df and "Iz" in df and "total_KE" in df and "N" in df:
        df_smooth["omega_MLE"] = df_smooth["total_L"]/df_smooth["Iz"]
        df_smooth["beta_MLE"] = (1/3 * (2 * df["total_KE"] + 
                                        df.omega_MLE**2 * df["Iz"] 
                                        - 2 * df["total_L"] * df.omega_MLE)/df["N"] )**-1 
    return df_smooth

def df_round_time(dfs, n=4):
    if isinstance(dfs, list):
        return [df_round_time(df, n) for df in dfs]
    else:
        df = dfs
        index = df.index
        return df.set_index(df.index.values.round(n))

def concat(dfs, key=None):
    if key is None:
        df = pd.concat([df for df in dfs],axis=1)
    else:
        df = pd.concat([df[key] for df in dfs],axis=1)
    df.columns = range(len(df.columns))
    return df
