#!/bin/bash
#SBATCH --job-name=hello-array
#SBATCH --partition=normal
#SBATCH --output=logs/hello_%A_%a.out
#SBATCH --error=logs/hello_%A_%a.err
#SBATCH --time=00:01:00
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1
#SBATCH --array=1-4                     # the new line, which says: run this script 4 times

# slurm/hello.slurm with one directive added. That single line turns one
# submission into four independent tasks, identical except for the task ID
# each one is handed. See Slurm Job Arrays.
#
# %A is the array's job ID and %a the task's index, so every task writes its
# own log rather than four tasks overwriting one file.
#
# Slurm resolves --output/--error when the job is submitted, relative to the
# directory you ran sbatch from — so logs/ must already exist there. The cd
# below only fixes paths used inside the script, not the log paths above.
#
# Run from the repo root:
#     mkdir -p logs
#     sbatch slurm/hello_array.slurm
#     cat logs/hello_<arrayid>_*.out
cd $HOME/gsb-research-computing-ai-skills

echo "Hello, world! My task number is $SLURM_ARRAY_TASK_ID"
