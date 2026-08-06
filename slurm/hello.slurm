#!/bin/bash
#SBATCH --job-name=hello
#SBATCH --partition=normal
#SBATCH --output=logs/hello_%j.out
#SBATCH --error=logs/hello_%j.err
#SBATCH --time=00:01:00
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1

# One script, one task — the baseline for the array demo on Slurm Job Arrays.
# Stripped of real work so the only thing on show is the shape of a submission.
# Pairs with slurm/hello_array.slurm, which is this script plus one directive.
#
# Slurm resolves --output/--error when the job is submitted, relative to the
# directory you ran sbatch from — so logs/ must already exist there. The cd
# below only fixes paths used inside the script, not the log paths above.
#
# Run from the repo root:
#     mkdir -p logs
#     sbatch slurm/hello.slurm
#     cat logs/hello_<jobid>.out
cd $HOME/gsb-research-computing-ai-skills

echo "Hello, world!"
