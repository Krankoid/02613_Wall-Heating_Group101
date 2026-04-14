#!/bin/bash
#BSUB -J parallelize
#BSUB -q hpc
#BSUB -n 16
#BSUB -W 24:00
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "rusage[mem=300MB]" # Roughly 300MB used 
#BSUB -oo parallel_times_%J.out
#BSUB -eo parallel_times_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

export PYTHONPATH="$PWD:$PYTHONPATH"
python -u parallelize.py 16 50
