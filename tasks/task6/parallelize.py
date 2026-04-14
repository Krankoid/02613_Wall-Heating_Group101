import sys
from os.path import join
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simulate import load_data, jacobi


# Run dynamic parallel execution of Jacobi method on multiple buildings 
# and measure wall time and elapsed times for each process.
# --- INPUT: n_procs, n_buildings ---
# --- OUTPUT: wall_times.npy, parallel_times.npy ---

# Apply Jacobi method to a list of building IDs
def apply_jacobi(bids):

    print(f"Process : {mp.current_process().pid}, handling building IDs: {bids}")

    if(type(bids) == str):
        bids = [bids]  # Convert to list if it's a single string

    start = perf_counter()
    # load data for each building assigned to this process and apply jacobi
    for bid in list(bids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    elapsed = perf_counter() - start

    return elapsed


if __name__ == '__main__':

    # Get number of processes and buildings to load from parsed arguments
    n_procs = int(sys.argv[1]) if len(sys.argv) > 1 else mp.cpu_count() # Defaults to all cores
    n_buildings = int(sys.argv[2]) if len(sys.argv) > 2 else 2 # Defaults to 2 buildings

    # Timing variables
    elapsed_times = np.ndarray([n_procs], dtype=object)  # elapsed times for each process 
    wall_time = [] # wall time for each process count

    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # Get building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()[:n_buildings]

        print(f"Using {n_procs} processes for dynamic parallel execution of {n_buildings} buildings")

        start_wall = perf_counter()
        # Run jacobi iterations in parallel with dynamic scheduling
        with mp.Pool(n_procs) as pool:
            elapsed_times_async = []
            # Fully parallelize by assigning each building to a separate process
            # This will force each process to handle one building at a time
            return_time = [pool.apply_async(apply_jacobi, args=([buildings])) for buildings in building_ids]
            elapsed_times_async.append(return_time)

            # Collect results
            pool.close()
            pool.join()
            elapsed_times = [rt.get() for sublist in elapsed_times_async for rt in sublist]
    
        # Calculate total elapsed time for this process count
        wall_time.append(perf_counter() - start_wall)
        print(f"Finished with {n_procs} processes in {wall_time[-1]:.2f} seconds")

    # Print and save results
    print(f"Elapsed times: {elapsed_times}")
    print(f"Wall times: {wall_time}")

    np.save('parallel_times.npy', elapsed_times)
    np.save('wall_times.npy', wall_time)