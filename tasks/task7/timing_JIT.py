from os.path import join
import sys
import numpy as np
from numba import jit
from time import perf_counter

from simulate import load_data, summary_stats

@jit(nopython=True)
def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u_old = u.copy()
    u_new = u.copy()

    nrows, ncols = u.shape

    for _ in range(max_iter):
        delta = 0.0

        # Loop row by row for cache-friendly access
        for i in range(1, nrows - 1):
            for j in range(1, ncols - 1):
                if interior_mask[i - 1, j - 1]:
                    new_val = 0.25 * (
                        u_old[i, j - 1] +   # left
                        u_old[i, j + 1] +   # right
                        u_old[i - 1, j] +   # up
                        u_old[i + 1, j]     # down
                    )

                    diff = abs(u_old[i, j] - new_val)
                    if diff > delta:
                        delta = diff

                    u_new[i, j] = new_val
                else:
                    u_new[i, j] = u_old[i, j]

        if delta < atol:
            break

        # Swap arrays instead of copying every iteration
        u_old, u_new = u_new, u_old

    return u_old

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
MAX_ITER = 20_000
ABS_TOL = 1e-4
TOTAL_BUILDINGS = 4571

if len(sys.argv) < 2:
    N = 10
else:
    N = int(sys.argv[1])

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()[:N]

# --- Dummy call to trigger JIT compilation ---
u0_dummy, mask_dummy = load_data(LOAD_DIR, building_ids[0])
_ = jacobi_jit(u0_dummy, mask_dummy, 1, ABS_TOL)

start = perf_counter()
for bid in building_ids:
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
elapsed = perf_counter() - start

sec_per_building = elapsed / N
estimated_total_hours = sec_per_building * TOTAL_BUILDINGS / 3600

print(f"N = {N} buildings")
print(f"Elapsed: {elapsed:.2f} s")
print(f"Per building: {sec_per_building:.2f} s")
print(f"Estimated total ({TOTAL_BUILDINGS} buildings): {estimated_total_hours:.1f} hours")