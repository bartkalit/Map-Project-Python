import numpy as np


n = 10
distances = np.empty((n,), dtype=np.ndarray)
for i in range(n):
    distances[i] = np.zeros((n, n))

