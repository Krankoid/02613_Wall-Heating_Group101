#!/bin/bash
#BSUB -J custom_cuda
#BSUB -q gpua100
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[gpu80gb]"
#BSUB -W 00:30
#BSUB -o output_%J.out
#BSUB -e error_%J.err



source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python -u custom_cuda.py 10