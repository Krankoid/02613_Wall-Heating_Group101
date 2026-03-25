import sys
from os.path import join
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simulate import load_data, jacobi

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
MAX_ITER = 20_000
ABS_TOL = 1e-4

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()[:3]

rows = len(building_ids)
fig, axes = plt.subplots(rows, 3, figsize=(14, 4 * rows), squeeze=False)

for row, bid in enumerate(building_ids):
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)

    ax = axes[row, 0]
    im = ax.imshow(u0[1:-1, 1:-1], cmap='inferno', vmin=0, vmax=25)
    ax.set_title(f'Building {bid}: initial domain')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax = axes[row, 1]
    ax.imshow(interior_mask, cmap='gray')
    ax.set_title(f'Building {bid}: interior mask')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    ax = axes[row, 2]
    im = ax.imshow(u[1:-1, 1:-1], cmap='inferno', vmin=5, vmax=25)
    ax.set_title(f'Building {bid}: converged temperature')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

fig.tight_layout()
fig.savefig('simulation_results.png', dpi=150)
print('Saved simulation_results.png')
