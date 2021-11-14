#!/usr/bin/env bash

#SBATCH --job-name=kvile_od
#SBATCH --time=0-500:00:00
# SBATCH --array=1,26,51,76,101


/opt/sif/conda.sif dep_env.yml plots_animations.py 
