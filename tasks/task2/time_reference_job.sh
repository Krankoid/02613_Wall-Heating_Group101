#!/bin/bash
#BSUB -J mini_ref_time
#BSUB -q hpc
#BSUB -n 1
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6126]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -o tasks/task2/reference_timing_%J.out
#BSUB -e tasks/task2/reference_timing_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

export PYTHONPATH="$PWD:$PYTHONPATH"
python -u tasks/task2/time_reference.py 10
