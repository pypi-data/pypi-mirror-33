import numpy as np


def dot_loss(w, l):
    return np.dot(w, l)


def mix_loss(w, l):
    return np.log(np.sum(w * np.exp(-l)))
