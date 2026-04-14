from os.path import join
import sys
from time import perf_counter

import numpy as np
from numba import cuda


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2), dtype=np.float32)
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy")).astype(np.float32)
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy")).astype(np.bool_)
    return u, interior_mask


@cuda.jit
def jacobi_kernel(u_old, u_new, interior_mask):
    # 2D thread index
    j, i = cuda.grid(2)

    # Check that this thread maps to a valid point in the 512x512 interior mask
    if i < interior_mask.shape[0] and j < interior_mask.shape[1]:
        # Map mask indices to the 514x514 grid
        ui = i + 1
        uj = j + 1

        # Update only true interior points
        if interior_mask[i, j]:
            u_new[ui, uj] = 0.25 * (
                u_old[ui, uj - 1] +   # left
                u_old[ui, uj + 1] +   # right
                u_old[ui - 1, uj] +   # up
                u_old[ui + 1, uj]     # down
            )
        else:
            # Keep non-interior points unchanged
            u_new[ui, uj] = u_old[ui, uj]


@cuda.jit
def copy_boundary_kernel(u_old, u_new):
    # 2D thread index for full 514x514 array
    j, i = cuda.grid(2)

    if i < u_old.shape[0] and j < u_old.shape[1]:
        if i == 0 or i == u_old.shape[0] - 1 or j == 0 or j == u_old.shape[1] - 1:
            u_new[i, j] = u_old[i, j]


def jacobi_cuda(u, interior_mask, max_iter):
    # Copy input to host arrays with GPU-friendly dtypes
    u = np.array(u, dtype=np.float32, copy=True)
    interior_mask = np.array(interior_mask, dtype=np.bool_, copy=False)

    # Copy arrays to GPU
    d_u_old = cuda.to_device(u)
    d_u_new = cuda.to_device(u)
    d_mask = cuda.to_device(interior_mask)

    # Threads per block
    tpb = (16, 16)

    # Blocks per grid for the 512x512 mask
    bpg_mask = (
        (interior_mask.shape[1] + tpb[0] - 1) // tpb[0],
        (interior_mask.shape[0] + tpb[1] - 1) // tpb[1],
    )

    # Blocks per grid for the full 514x514 grid
    bpg_u = (
        (u.shape[1] + tpb[0] - 1) // tpb[0],
        (u.shape[0] + tpb[1] - 1) // tpb[1],
    )

    # Fixed number of Jacobi iterations (task 8: no early stopping)
    for _ in range(max_iter):
        jacobi_kernel[bpg_mask, tpb](d_u_old, d_u_new, d_mask)
        copy_boundary_kernel[bpg_u, tpb](d_u_old, d_u_new)
        d_u_old, d_u_new = d_u_new, d_u_old # Swap old/new arrays instead of copyin

    cuda.synchronize()
    return d_u_old.copy_to_host()


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
    TOTAL_BUILDINGS = 4571
    
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])

    building_ids = building_ids[:N]

    #Warm up GPU by running one iteration on the first building (if N>0)
    if N > 0:
        u0, interior_mask = load_data(LOAD_DIR, building_ids[0])
        _ = jacobi_cuda(u0, interior_mask, 1)

    start = perf_counter()

    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi_cuda(u0, interior_mask, MAX_ITER)

        stats = summary_stats(u, interior_mask)

    cuda.synchronize() # Ensure all GPU work is done before stopping the timer
    elapsed = perf_counter() - start
    sec_per_building = elapsed / N
    estimated_total_hours = sec_per_building * TOTAL_BUILDINGS /3600

    print(f"N = {N} buildings")
    print(f"Elapsed: {elapsed:.2f} s")
    print(f"Per building: {sec_per_building:.2f} s")
    print(f"Estimated total ({TOTAL_BUILDINGS} buildings): {estimated_total_hours:.1f} hours")

   
   