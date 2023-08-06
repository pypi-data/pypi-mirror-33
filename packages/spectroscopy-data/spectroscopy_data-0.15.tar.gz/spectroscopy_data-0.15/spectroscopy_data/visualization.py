import numpy as np
from .utils import gaussian_2D


def get_multicolors():
    x = np.linspace(-10, 10, 200)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x,y)
    colors = [
              [{"A":4,"m_x":-6, "m_y": -1, "sigma_a":1, "sigma_b":1, "theta":0},
               {"A":1,"m_x":-3, "m_y": 2, "sigma_a":2, "sigma_b":2, "theta":0},
               {"A":1,"m_x":2, "m_y": 3, "sigma_a":2, "sigma_b":1, "theta":0}],
              [{"A":2,"m_x":0, "m_y":0, "sigma_a":5, "sigma_b":3, "theta":45},
               {"A":2,"m_x":-2, "m_y":1, "sigma_a":2, "sigma_b":2, "theta":90}],
              [{"A":4,"m_x":-6, "m_y": -1, "sigma_a":1, "sigma_b":1, "theta":0},
               {"A":2,"m_x":-2, "m_y":2, "sigma_a":1, "sigma_b":1, "theta":45},
               {"A":2,"m_x":2, "m_y":-3, "sigma_a":4, "sigma_b":4, "theta":75}]
              ]
    output = np.zeros(list(X.shape)+[len(colors)])
    for idx, color in enumerate(colors):
        for gauss in color:
            output[:,:,idx] += gaussian_2D(X,Y,**gauss)
    return X, Y, np.round(output)
