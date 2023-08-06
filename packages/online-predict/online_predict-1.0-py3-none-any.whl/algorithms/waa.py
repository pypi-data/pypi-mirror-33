from algorithms.algorithm import Algorithm
import numpy as np


class WAA(Algorithm):
    def __init__(self, n: 'The number of experts', loss: 'Loss function(pt, yt)', l: 'Learning rate'):
        super().__init__(n, loss)
        self._w = [np.ones(n) / n]
        self._l = l

    def update(self, x, y):
        super().update(x, y)
        self._update_weight(x, y)

    def _update_weight(self, z, y):
        t = len(self._w) - 1
        w = self._w[t]
        new_w = np.zeros(self._n)
        for i in range(self._n):
            new_w[i] = w[i] * np.exp(-self._l * self._loss(z[i], y))
        new_w /= np.sum(new_w)
        self._w.append(new_w)
