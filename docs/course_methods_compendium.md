# Course Methods Compendium for the Wall Heating Project

This file is the project anchor for how we should approach the wall heating mini-project based on the solved course material in weeks 1-6.

The point is not just to get a fast solution. The point is to solve the project in a way that matches the course learning objectives, tooling, and style already used in this repo.

## Scope

This compendium is based on the solved material in:

- `week01_intro-to-pyhpc`
- `week02_python-bootcamp`
- `week03_memory-hierarchy`
- `week04_profiling-and-high-performance-numpy`
- `week05_parallelism-part-1`
- `week06_parallelism-part-2`

It is intentionally limited to methods that are already part of the course progression up through week 6.

That means:

- CPU-side Python, NumPy, profiling, cache reasoning, batch jobs, multiprocessing, Amdahl analysis, chunking, and NUMA awareness are in scope.
- Numba CPU JIT, CUDA kernels, and CuPy are not part of this compendium yet, because those belong to later course weeks.

## Core rule for this project

When we propose a solution for the wall heating project, the default order of attack should be:

1. Get a correct baseline that matches the reference script.
2. Run it on HPC using the course job-script style.
3. Measure runtime on a controlled CPU model.
4. Profile before changing the implementation.
5. Prefer NumPy and data-layout improvements before more exotic changes.
6. When parallelizing, start with multiprocessing across floorplans.
7. Measure speedup and estimate parallel fraction with Amdahl's law.
8. If work per floorplan varies, move from static work splitting to chunked or dynamic scheduling.

That progression is directly aligned with the weeks 1-6 solved material.

## Week 1: HPC workflow and batch jobs

### Methods and tools extracted

- Log into the DTU cluster with `ssh`.
- Move to a Linux shell with `linuxsh`.
- Activate the course conda environment with:
  - `source /dtu/projects/02613_2025/conda/conda_init.sh`
  - `conda activate 02613`
- Use LSF batch scripts with `#BSUB` directives.
- Always specify at least:
  - job name
  - queue
  - wall time
  - stdout file
  - stderr file
- For reproducible timings, request a specific CPU model with:
  - `#BSUB -R "select[model==...]"`.
- For multi-core CPU jobs on one node, request:
  - `#BSUB -n <cores>`
  - `#BSUB -R "span[hosts=1]"`.
- Inspect and manage jobs with:
  - `bsub`
  - `bjobs`
  - `bjobs -p`
  - `bpeek`
  - `bkill`
- Use `lscpu` and scheduler metadata to document the runtime environment.

### What this means for the wall heating project

- All serious timing should be done as HPC batch jobs, not interactively on a laptop.
- Timings should use a fixed CPU model whenever possible.
- Every important project step should leave behind reproducible artifacts:
  - `.out`
  - `.err`
  - plots
  - CSV files

### Concrete pattern we should reuse

For any new project timing job:

```bash
#!/bin/bash
#BSUB -J some_job_name
#BSUB -q hpc
#BSUB -n 1
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6126]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -o some_job_%J.out
#BSUB -e some_job_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python -u script.py
```

## Week 2: Basic Python and NumPy program structure

### Methods and tools extracted

- Keep scripts simple and explicit.
- Use command-line arguments via `sys.argv` or `argparse`.
- Use `numpy.load` and `numpy.save` for `.npy` files.
- Use NumPy reductions and array operations directly:
  - `mean`
  - `std`
  - `linalg.norm`
  - matrix multiplication with `@`
- Use `time.perf_counter()` for timing.
- Separate input parsing, computation, and output in a straightforward way.

### Style lessons from the solved material

- Small CLI tools are acceptable and expected.
- The repo style is direct rather than abstract.
- Data is often saved as `.npy` or printed to stdout for later collection.

### What this means for the wall heating project

- Project scripts should stay as small, inspectable programs.
- Prefer clear helper functions like:
  - `load_data`
  - `jacobi`
  - `summary_stats`
  - `run_simulation`
- Save structured outputs in machine-readable formats:
  - CSV for per-building statistics
  - PNG for plots
- Use `perf_counter()` for all timing measurements.

## Week 3: Memory hierarchy, access patterns, and measurement

### Methods and tools extracted

- Performance depends strongly on memory access patterns.
- Row-wise contiguous access is usually faster than strided access.
- Plot performance against working-set size.
- Interpret changes using cache sizes.
- Use repeated timings and sweeps instead of single anecdotes.
- Compare alternatives empirically.
- Distinguish compute cost from memory and I/O cost.

### Concrete lessons from the solved set

- Use log-log performance plots when sweeping problem size.
- Annotate cache levels when relevant.
- Do not assume "more vectorized" automatically means "faster".
- Large temporary arrays can make a nominally elegant NumPy version slower.
- The correct question is not "is NumPy good?" but "what is this version doing to memory traffic?"

### What this means for the wall heating project

For the Jacobi solver, week 3 is directly relevant:

- The solver repeatedly updates a 2D grid, so memory access pattern matters.
- We should be suspicious of versions that create large temporaries every iteration.
- We should compare:
  - the baseline vectorized implementation
  - more careful variants with fewer temporaries
  - later, compiled or parallel versions
- Any claim about one implementation being faster must be backed by measurement.

### Practical guidance for this project

- Use fixed CPU models when timing.
- Use the same subset size when comparing implementations.
- If two implementations differ mainly in memory behavior, explain them in cache terms.
- For the wall-heating project, the interior-mask indexing step is a likely hotspot because it introduces masked gathers/scatters and extra temporary arrays.

## Week 4: Profiling before optimization, and careful NumPy use

### Methods and tools extracted

- Use `cProfile` to find high-level hotspots.
- Use `line_profiler` / `kernprof` to identify expensive lines inside a function.
- Optimize based on measured hotspots, not guesses.
- Reduce repeated work by hoisting invariant computations out of loops.
- Use NumPy broadcasting and vectorized array operations where they help.
- But do not blindly remove all loops if doing so creates huge temporary arrays.

### Key lessons from the solved material

- Moving from two nested Python loops to one loop plus NumPy operations can help a lot.
- Precomputing repeated quantities can give meaningful speedups.
- A fully no-loop NumPy version is not always best if the intermediate arrays become too large.
- Line profiling tells you where to focus, not just whether the whole function is slow.

### What this means for the wall heating project

Before changing the Jacobi solver substantially, we should:

1. Profile the reference `jacobi`.
2. Identify the dominant lines.
3. Focus on:
   - neighbor averaging
   - masked extraction / assignment
   - convergence checking
4. Only then decide whether to:
   - keep NumPy style and reduce temporaries
   - restructure loops
   - change data layout

### Week-4-compliant optimization ideas for wall heating

These are in scope because they follow the week 4 pattern:

- Hoist invariant views or masks outside repeated work where possible.
- Avoid recomputing values that do not change across iterations.
- Compare:
  - full-array updates
  - masked updates
  - one-loop-over-floorplans plus vectorized inner work
- Treat "fully vectorized" as a candidate, not an automatic winner.

### Methods we should avoid at this stage

Until later project tasks explicitly call for them, week 4 suggests avoiding:

- jumping straight to exotic acceleration without profiling
- assuming no-loop NumPy is always optimal
- claiming wins without profiler output and timing data

## Week 5: CPU multiprocessing and Amdahl analysis

### Methods and tools extracted

- Use `multiprocessing.Pool` for CPU parallelism.
- Compare naïve fine-grained tasks with chunked tasks.
- `apply_async` can be better than overly fine-grained `map` for tiny tasks.
- Measure speedup as a function of process count.
- Use Amdahl's law to estimate:
  - parallel fraction
  - theoretical maximum speedup

### Core lesson from the solved material

Parallel overhead matters.
If the work units are too small, process-management overhead can dominate.
Chunking independent work into larger tasks improves performance.

### What this means for the wall heating project

The most course-aligned first parallelization is:

- parallelize across floorplans, not within one floorplan

Why:

- floorplans are naturally independent units of work
- this matches the project wording
- this matches the week 5 strategy of independent task parallelism

### Static scheduling pattern for the wall heating project

For the first multiprocessing version:

- split the list of building IDs into equally sized chunks
- assign one chunk per worker
- let each worker process its assigned floorplans sequentially
- combine the resulting CSV rows at the end

This is the week-5 style answer to the project task that explicitly asks for static scheduling.

### Required evaluation for any such implementation

- runtime vs number of workers
- speedup plot
- Amdahl-style fitted parallel fraction
- maximum theoretical speedup
- estimate for full-dataset runtime

## Week 6: Load balance, chunking, dynamic scheduling, NUMA awareness

### Methods and tools extracted

- If per-task runtime varies, static equal splitting can be suboptimal.
- Use more chunks than workers to improve load balance.
- Dynamic or chunked scheduling helps when task costs are heterogeneous.
- Repeat each timing several times and use an average.
- Be aware that performance can degrade at high core counts because of memory-system effects and NUMA.
- Use `numactl --interleave=all` when relevant to test NUMA effects.

### Core lessons from the solved material

- Equal numbers of tasks per process does not imply equal runtime.
- Dynamic chunking improves utilization when some tasks are much slower than others.
- Scaling can flatten or even worsen beyond a certain number of cores.
- Python multiprocessing can be limited by memory traffic and overhead.

### What this means for the wall heating project

This is directly relevant because the project text itself states that:

- different floorplans may require different numbers of iterations to converge

That means:

- static scheduling is the right first experiment
- dynamic scheduling is the right second experiment

For the project, week 6 suggests:

- start with one chunk per worker for the required static version
- then introduce smaller chunks than workers for the dynamic version
- compare both speed and speedup
- explain improved performance by better load balance

### Additional week-6-relevant caution

The wall-heating solver is memory intensive.
So if scaling stops improving at higher process counts, the explanation may be:

- memory bandwidth saturation
- NUMA effects
- process overhead
- too many workers for the problem size

That explanation is course-aligned and should be preferred over vague statements.

## Project-specific method map

This section maps the course material to the wall-heating project tasks.

### Task 1: inspect the data

Use:

- week 2 style NumPy I/O
- simple plotting scripts
- week 1 HPC workflow only if data access is on the cluster

Expected artifacts:

- input plots
- short explanation of domain arrays and interior masks

### Task 2: baseline timing

Use:

- week 1 batch scripts
- week 2 `perf_counter`
- week 3 controlled measurement on fixed CPU model

Expected artifacts:

- `.out` and `.err` job files
- baseline runtime for a small subset
- full-runtime estimate

### Task 3: visualize results

Use:

- week 2 script structure
- simple NumPy-based solver invocation
- saved PNG outputs

### Task 4: profile the reference `jacobi`

Use:

- week 4 `cProfile`
- week 4 `line_profiler` / `kernprof`

Expected outcome:

- a precise statement of what lines dominate runtime

### Task 5: static parallelization over floorplans

Use:

- week 5 multiprocessing
- equal static work assignment
- speedup plotting
- Amdahl fitting

Expected outcome:

- speedup curve
- estimated parallel fraction
- estimate of full-dataset runtime

### Task 6: dynamic scheduling

Use:

- week 6 chunked or dynamic task assignment
- explanation based on unequal convergence cost across floorplans

Expected outcome:

- faster or better-balanced parallel execution than the static version

## Default toolbox we should use in project suggestions

When proposing next steps for this project, the default toolbox should be:

- `ssh`, `linuxsh`, DTU course conda environment
- LSF job scripts with `bsub`
- `perf_counter`
- `numpy.load`, `numpy.save`
- NumPy array slicing and reductions
- matplotlib for plots
- CSV outputs for measurements
- `cProfile`
- `kernprof` / `line_profiler`
- `multiprocessing.Pool`
- chunked work distribution
- speedup plots
- Amdahl-law reasoning
- optional `numactl --interleave=all` for later CPU scaling investigations

## Methods that are not yet the default

These may become relevant later in the project, but they should not be my default suggestions while we are staying anchored to weeks 1-6:

- Numba JIT
- CUDA kernels
- CuPy
- GPU-first solutions
- advanced external frameworks not used in the course material

If we use them later, it should be because the project task explicitly asks for them or because later course weeks have covered them.

## Decision rules for future wall-heating suggestions

When suggesting a solution, prefer the first matching rule:

1. If the task is about correctness, use the simplest week 2 style NumPy/Python solution that matches the reference.
2. If the task is about timing, use a week 1 HPC batch job with a fixed CPU model.
3. If the task is about why code is slow, use week 4 profiling before rewriting.
4. If the task is about CPU performance of array code, reason in week 3 cache and temporary-array terms.
5. If the task is about using more cores, start with week 5 multiprocessing over floorplans.
6. If load varies between floorplans, switch to week 6 chunked or dynamic scheduling.
7. Only go beyond this compendium when the relevant later course material has been covered or the project task explicitly requires it.

## Bottom line

For the wall-heating project, the course-consistent path through weeks 1-6 is:

- baseline script on HPC
- controlled timing
- profiling
- careful NumPy optimization
- static multiprocessing over independent floorplans
- speedup measurement and Amdahl analysis
- dynamic scheduling when iteration counts vary

That is the methodology this project should follow unless a later project task explicitly requires a later-week technique.
