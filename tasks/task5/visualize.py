import numpy as np
import matplotlib.pyplot as plt

ax = plt.subplot(11, projection='3d')
y = np.load('parallel_times.npy')
x = np.arange(1, len(y) + 1)
plt.plot(x,y, marker='o', label='Parallel Execution Time')

plt.savefig('parallel_execution_times.png')
