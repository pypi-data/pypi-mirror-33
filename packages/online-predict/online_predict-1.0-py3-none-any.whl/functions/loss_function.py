import numpy as np


def square(y, x):
    return (y - x) ** 2


def logarithmic(y, x):
    return (1 - y) * np.log((1 - y) / (1 - x)) + y * np.log(y / x)


def hellinger(y, x):
    return ((np.sqrt(1 - y) - np.sqrt(1 - x)) ** 2 + (np.sqrt(y) - np.sqrt(x)) ** 2) / 2


def absolute(y, x):
    return np.abs(y - x)
