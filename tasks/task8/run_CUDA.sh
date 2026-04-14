#!/bin/bash
#BSUB -J custom_cuda
#BSUB -q c02613
#BSUB -n 4
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 30
#BSUB -R "rusage[mem=8GB]"
#BSUB -o output_%J.out
#BSUB -e error_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python -u custom_CUDA.py 10