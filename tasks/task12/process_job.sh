#!/bin/bash
#BSUB -J mini_process
#BSUB -q hpc
#BSUB -n 12
#BSUB -W 00:45
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model==XeonGold6126]"
#BSUB -R "rusage[mem=150MB]"
#BSUB -o tasks/task12/process_floorplans_%J.out
#BSUB -e tasks/task12/process_floorplans_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

export PYTHONPATH="$PWD:$PYTHONPATH"

python -u tasks/task12/process_floorplans.py 12 4571
