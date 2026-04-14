import numpy as np
import matplotlib.pyplot as plt

y = np.load('wall_times.npy')
x = np.arange(1, len(y) + 1)
ax = plt.subplot(111)
ax.plot(x,y[0]/y, marker='o', 
         label='Parallel Execution Time')
ax.set_xlabel('Number of Processes')
ax.set_ylabel('Speedup')
ax.set_title('Speedup of Parallel Execution')
ax.set_xticks(x)

plt.savefig('parallel_execution_times.png')
