import matplotlib.pyplot as plt
import numpy as np

labels = [
    'Reference\n(NumPy, 1 core)',
    'Numba JIT\n(Task 7, 1 core)',
    'Custom CUDA\n(Task 8, GPU)',
    'Naive CuPy\n(Task 9, GPU)',
    'Optimized CuPy\n(Task 10, GPU)',
]
times = [12.01, 1.88, 1.52, 2.45, 1.15]
colors = ['#d9534f', '#f0ad4e', '#5bc0de', '#5bc0de', '#5cb85c']

x = np.arange(len(labels))
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(x, times, color=colors, width=0.55, edgecolor='white')

ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel('Time per building (s)')
ax.set_title('Per-building runtime across implementations (N = 10 buildings)')
ax.set_ylim(0, 14)

for bar, t in zip(bars, times):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
            f'{t:.2f} s', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('timing_comparison.png', dpi=150)
print('Saved timing_comparison.png')
