#-*-coding: utf-8 -*-
#author:tyhj
#tools.py 2017/8/15 15:05
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_3dbar(portEret, var1, var2):
    avg = pd.DataFrame(portEret.mean().values.reshape(5, 5), index=range(1, 6), columns=range(1, 6))
    avg.index.name = var1

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel(var1, )
    ax.set_ylabel(var2)
    ax.set_zlabel("avgEret")
    ax.set_xlim3d(0, 6)
    ax.set_ylim3d(0, 6)

    avg = portEret.mean()
    n = len(avg)

    xpos = [int(float(ind)) / 10 for ind in avg.index]
    ypos = [int(float(ind)) % 10 for ind in avg.index]
    zpos = np.zeros(n)

    dx = np.ones(n) / 4
    dy = np.ones(n) / 4
    dz = avg.values

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='y')

    plt.gca().invert_xaxis()
    plt.show()

    return fig


def get_3dline(portEret, var1, var2):
    # portEret=pd.read_csv(r'D:\quantDb\researchTopics\crossSection\data\portEret.csv',index_col=0)
    avg = pd.DataFrame(portEret.mean().values.reshape(5, 5), index=range(1, 6), columns=range(1, 6))
    X = [[i] * 5 for i in range(1, 6)]
    Y = [range(1, 6) for i in range(5)]
    Z = avg.values

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1)

    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    ax.set_zlabel("avgEret")
    return fig

    # rotate the axes and update
    # for angle in range(0, 360):
    #     ax.view_init(30, angle)
    #     plt.draw()
    #     plt.pause(.001)















