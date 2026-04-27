from os.path import join
import sys
from time import perf_counter

import numpy as np
import cupy as cp


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi_cupy_optimized(u, interior_mask, max_iter, atol=1e-6):
    # cp.where replaces boolean-mask indexing throughout — including the delta
    # computation — so no boolean fancy indexing triggers per-iteration DtoH copies.
    d_u = cp.asarray(u)
    d_mask = cp.asarray(interior_mask)

    for _ in range(max_iter):
        u_new = 0.25 * (
            d_u[1:-1, :-2] + d_u[1:-1, 2:] +
            d_u[:-2, 1:-1] + d_u[2:, 1:-1]
        )
        delta = float(cp.where(d_mask, cp.abs(u_new - d_u[1:-1, 1:-1]), 0).max())
        d_u[1:-1, 1:-1] = cp.where(d_mask, u_new, d_u[1:-1, 1:-1])

        if delta < atol:
            break

    cp.cuda.runtime.deviceSynchronize()
    return cp.asnumpy(d_u)


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    TOTAL_BUILDINGS = 4571

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 10
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    start = perf_counter()
    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi_cupy_optimized(u0, interior_mask, MAX_ITER, ABS_TOL)
        stats = summary_stats(u, interior_mask)
    cp.cuda.runtime.deviceSynchronize()
    elapsed = perf_counter() - start

    sec_per_building = elapsed / N
    estimated_total_hours = sec_per_building * TOTAL_BUILDINGS / 3600

    print(f"N = {N} buildings")
    print(f"Elapsed: {elapsed:.2f} s")
    print(f"Per building: {sec_per_building:.2f} s")
    print(f"Estimated total ({TOTAL_BUILDINGS} buildings): {estimated_total_hours:.1f} hours")
