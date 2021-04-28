
import numpy as np
import matplotlib.pyplot as plt


def plot_depht():
    depths = np.load("depths.npy")
    centersx = np.load("centersx.npy")
    centersz = np.load("centersz.npy")
    xs = np.load("xs.npy")

    plt.plot(xs, depths, color='r', label='depth')
    plt.plot(xs, centersx, color='g', label='x')
    plt.plot(xs, centersz, color='b', label='z')

    plt.xlabel('Frame')
    plt.ylabel('Profondeur et centre des x et z')
    plt.title='Profondeur et centre lissés'
    plt.grid()

    plt.savefig("depth_center.png")
    plt.legend()
    plt.show()


plot_depht()
