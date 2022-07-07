from IPython.display import Audio

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
    return Audio(sound_file, autoplay=True) 