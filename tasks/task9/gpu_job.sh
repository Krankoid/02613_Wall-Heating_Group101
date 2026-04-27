#!/bin/bash
#BSUB -J cupy_jacobi
#BSUB -q c02613
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o tasks/task9/cupy_jacobi_%J.out
#BSUB -e tasks/task9/cupy_jacobi_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

export PYTHONPATH="$PWD:$PYTHONPATH"
python -u tasks/task9/simulate_cupy.py 10
