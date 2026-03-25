# HPC Mini-Project 101 - Wall Heating

Simulate steady-state heat distribution across 4571 building floorplans using the Jacobi method, then benchmark and optimize the solver.

---

## 1. Connect to HPC

Run these in your **local terminal** (VS Code or otherwise):

```bash
ssh <yourstudentid>@login.hpc.dtu.dk
```

```bash
linuxsh
```

```bash
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613
```

```bash
cd ~/HPC-mini-project-101
```

All commands below assume you are in `~/HPC-mini-project-101`.

---

## 2. Transfer files with FileZilla

**FileZilla connection:** `sftp://login.hpc.dtu.dk`, port `22`, your DTU credentials.

### Upload (local → HPC)

Recreate this structure under `~/HPC-mini-project-101/` on the HPC side:

```
HPC-mini-project-101/
├── simulate.py
└── tasks/
    ├── task1/
    │   └── inspect_floorplans.py
    ├── task2/
    │   ├── time_reference.py
    │   └── time_reference_job.sh
    ├── task3/
    │   └── visualize_simulation_results.py
    └── task4/
        ├── profile_jacobi.py
        └── profile_jacobi_job.sh
```

> `simulate.py` must be at the root - all task scripts import from it.

### Download (HPC → local) after each task

| HPC file | Save locally to |
|---|---|
| `~/HPC-mini-project-101/floorplan_inputs.png` | `tasks/task1/` |
| `~/HPC-mini-project-101/tasks/task2/reference_timing_*.out/err` | `tasks/task2/` |
| `~/HPC-mini-project-101/simulation_results.png` | `tasks/task3/` |
| `~/HPC-mini-project-101/tasks/task4/reference_jacobi_profile_*.out/err` | `tasks/task4/` |

---

## 3. Task 1 - Visualize input floorplans

Loads 4 example buildings and saves a figure of their domain grids and interior masks.

```bash
python tasks/task1/inspect_floorplans.py
```

Output: `floorplan_inputs.png` in the working directory. Download via FileZilla.

---

## 4. Task 2 - Time the reference implementation

Submits a batch job that times the reference solver on 10 buildings and extrapolates to the full dataset.

```bash
bsub < tasks/task2/time_reference_job.sh
```

Check job status:

```bash
bjobs
```

Once the job shows `DONE`, read the results:

```bash
cat tasks/task2/reference_timing_*.out
```

Output: `tasks/task2/reference_timing_<jobid>.out` and `.err`. Download both via FileZilla.

---

## 5. Task 3 - Visualize simulation results

Runs the Jacobi solver on 3 buildings and saves a figure showing initial state and converged temperature fields.

```bash
python tasks/task3/visualize_simulation_results.py
```

> This takes a few minutes - run it on `linuxsh`, not the login node.

Output: `simulation_results.png`. Download via FileZilla.

---

## 6. Task 4 - Profile the Jacobi function

Submits a batch job that runs `kernprof` line-profiler on the `jacobi` function for 1 building.

```bash
bsub < tasks/task4/profile_jacobi_job.sh
```

Check job status:

```bash
bjobs
```

Once done, read the profiler output in the terminal with the cat command, or just transfer it back locally and view it there:

```bash
cat tasks/task4/reference_jacobi_profile_*.out
```

Output: `tasks/task4/reference_jacobi_profile_<jobid>.out` and `.err`. Download both via FileZilla.

---

## Quick reference

```bash
# Connect
ssh s204749@login.hpc.dtu.dk
linuxsh
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613
cd ~/HPC-mini-project-101

# Task 1
python tasks/task1/inspect_floorplans.py

# Task 2
bsub < tasks/task2/time_reference_job.sh
bjobs
cat tasks/task2/reference_timing_*.out

# Task 3
python tasks/task3/visualize_simulation_results.py

# Task 4
bsub < tasks/task4/profile_jacobi_job.sh
bjobs
cat tasks/task4/reference_jacobi_profile_*.out
```
