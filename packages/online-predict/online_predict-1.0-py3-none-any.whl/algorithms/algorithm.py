import numpy as np


class Algorithm:
    def __init__(self, n: 'The number of experts', loss: 'Loss function(pt, yt)'):
        self._n = n
        self._loss = loss
        self._w = []
        self._p = []

    def update(self, x, y):
        self._p.append(self.predict(x))

    def predict(self, x):
        w = self._w[-1]
        p = np.zeros_like(w)
        for i in range(self._n):
            p += w[i] * x[i]
        return p
