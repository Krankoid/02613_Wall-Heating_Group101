import sys
from os.path import join
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simulate import load_data, jacobi

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
MAX_ITER = 20_000
ABS_TOL = 1e-4
EXCLUDE = {'10000', '10019', '10029', '10334', '10786', '11117'}

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    all_ids = f.read().splitlines()

building_ids = [bid for bid in all_ids if bid not in EXCLUDE][:4]

fig, axes = plt.subplots(1, 4, figsize=(16, 5), squeeze=False, constrained_layout=True)

for col, bid in enumerate(building_ids):
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)

    axes[0, col].set_title(f'Building {bid}')
    im = axes[0, col].imshow(u[1:-1, 1:-1], cmap='inferno', vmin=5, vmax=25)

fig.colorbar(im, ax=axes[0, :].tolist(), fraction=0.02, pad=0.04)
fig.savefig('fixed_simulation_results.png', dpi=150)
print('Saved fixed_simulation_results.png')
