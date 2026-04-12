#!/bin/bash
#BSUB -J mini_JIT_parallel
#BSUB -q hpc
#BSUB -n 18
#BSUB -W 00:30
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model==XeonGold6126]"
#BSUB -R "rusage[mem=150MB]"
#BSUB -o tasks/task11/timing_JIT_parallel_%J.out
#BSUB -e tasks/task11/timing_JIT_parallel_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

export PYTHONPATH="$PWD:$PYTHONPATH"

python -u tasks/task11/timing_JIT_parallel.py 18 360
