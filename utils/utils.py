import numpy as np

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
    return timedelta(seconds=(1.1e-7 * np.maximum(5e3,  n**2)*1.1))

def memory_estimate(n):
    """
    memory needed for single record in MegaBytes
    n : particle number
    """
    return (70 * n) / 1024**2

def plot_mean_std(df, color, label):
    from matplotlib import pyplot as plt

    m = df.mean(axis=1)
    std = df.std(axis=1)
    m.plot(color=color, label=label)
    plt.fill_between(df.index, (m + std), (m - std), color=color, alpha=0.1)