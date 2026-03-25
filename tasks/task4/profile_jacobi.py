from os.path import join

from simulate import load_data, jacobi, summary_stats

try:
    profile # type: ignore
except NameError:
    def profile(func):
        return func

jacobi = profile(jacobi)

LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
MAX_ITER = 20_000
ABS_TOL = 1e-4

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()[:1]

for bid in building_ids:
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
    print(bid, stats)
