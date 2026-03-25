#!/bin/bash
#BSUB -J mini_profile_jacobi
#BSUB -q hpc
#BSUB -n 1
#BSUB -W 00:20
#BSUB -R "select[model==XeonGold6126]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -o tasks/task4/reference_jacobi_profile_%J.out
#BSUB -e tasks/task4/reference_jacobi_profile_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

export PYTHONPATH="$PWD:$PYTHONPATH"
kernprof -l -v tasks/task4/profile_jacobi.py
