#!/bin/bash
#BSUB -J cupy_nsys
#BSUB -q c02613
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o tasks/task10/cupy_nsys_%J.out
#BSUB -e tasks/task10/cupy_nsys_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

export PYTHONPATH="$PWD:$PYTHONPATH"

# Profile the naive CuPy solution (task 9). 2 buildings is enough to see the
# pattern and keeps the .nsys-rep file small.
nsys profile -o tasks/task10/cupy_naive --force-overwrite true \
    python -u tasks/task9/simulate_cupy.py 2

nsys stats tasks/task10/cupy_naive.nsys-rep > tasks/task10/cupy_naive_stats.txt

# Profile the optimized CuPy solution (task 10) so we can confirm the fix.
nsys profile -o tasks/task10/cupy_opt --force-overwrite true \
    python -u tasks/task10/simulate_cupy_optimized.py 2

nsys stats tasks/task10/cupy_opt.nsys-rep > tasks/task10/cupy_opt_stats.txt
