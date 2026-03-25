from os.path import join
import sys
from time import perf_counter

from simulate import load_data, jacobi, summary_stats

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

start = perf_counter()
for bid in building_ids:
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
elapsed = perf_counter() - start

sec_per_building = elapsed / N
estimated_total_hours = sec_per_building * TOTAL_BUILDINGS / 3600

print(f"N = {N} buildings")
print(f"Elapsed: {elapsed:.2f} s")
print(f"Per building: {sec_per_building:.2f} s")
print(f"Estimated total ({TOTAL_BUILDINGS} buildings): {estimated_total_hours:.1f} hours")
