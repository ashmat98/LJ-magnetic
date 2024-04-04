from matplotlib import pyplot as plt
import matplotlib

plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = (3.5,2.5)

params = {"ytick.color" : "black",
          "xtick.color" : "black",
          "axes.labelcolor" : "black",
          "axes.edgecolor" : "black",
          "text.usetex" : True,
          "font.family" : "serif",
          "font.serif" : ["Computer Modern Serif"]}
plt.rcParams.update(params)
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']