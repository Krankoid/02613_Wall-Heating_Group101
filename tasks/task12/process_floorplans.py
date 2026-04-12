from os.path import join
import sys
import multiprocessing as mp
from time import perf_counter

import numpy as np
from numba import jit

from simulate import load_data, summary_stats


@jit(nopython=True)
def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u_old = u.copy()
    u_new = u.copy()

    nrows, ncols = u.shape

    for _ in range(max_iter):
        delta = 0.0

        for i in range(1, nrows - 1):
            for j in range(1, ncols - 1):
                if interior_mask[i - 1, j - 1]:
                    new_val = 0.25 * (
                        u_old[i, j - 1] +
                        u_old[i, j + 1] +
                        u_old[i - 1, j] +
                        u_old[i + 1, j]
                    )

                    diff = abs(u_old[i, j] - new_val)
                    if diff > delta:
                        delta = diff

                    u_new[i, j] = new_val
                else:
                    u_new[i, j] = u_old[i, j]

        if delta < atol:
            break

        u_old, u_new = u_new, u_old

    return u_old


def apply_jacobi_jit(bids):
    if isinstance(bids, str):
        bids = [bids]

    start = perf_counter()

    for bid in bids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
        _ = summary_stats(u, interior_mask)

    elapsed = perf_counter() - start
    return elapsed


if __name__ == "__main__":
    max_procs = int(sys.argv[1]) if len(sys.argv) > 1 else mp.cpu_count()
    n_buildings = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    LOAD_DIR = "/dtu/projects/02613_2025/data/modified_swiss_dwellings/"
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    TOTAL_BUILDINGS = 4571

    with open(join(LOAD_DIR, "building_ids.txt"), "r") as f:
        building_ids = f.read().splitlines()[:n_buildings]

    n_procs = min(max_procs, len(building_ids))
    print(f"--- Running with {n_procs} processes ---")

    chunk_size = (len(building_ids) + n_procs - 1) // n_procs
    chunks = []

    for i in range(n_procs):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, len(building_ids))
        if start_idx < len(building_ids):
            chunks.append(building_ids[start_idx:end_idx])

    start = perf_counter()
    with mp.Pool(n_procs) as pool:
        worker_times = pool.map(apply_jacobi_jit, chunks)
    elapsed = perf_counter() - start

    print(f"Worker times: {worker_times}")
    print(f"Total elapsed: {elapsed:.2f} s")
    
    N = n_buildings
    sec_per_building = elapsed / N
    estimated_total_hours = sec_per_building * TOTAL_BUILDINGS / 3600

    print(f"\nN = {N} buildings")
    print(f"Elapsed: {elapsed:.2f} s")
    print(f"Per building: {sec_per_building:.2f} s")
    print(f"Estimated total ({TOTAL_BUILDINGS} buildings): {estimated_total_hours:.1f} hours")