#!/bin/bash
#SBATCH --job-name=chain-step2
#SBATCH --partition=normal
#SBATCH --output=logs/chain_step2_%j.out
#SBATCH --error=logs/chain_step2_%j.err
#SBATCH --time=00:05:00
#SBATCH --mem=1G
#SBATCH --cpus-per-task=1

cd $HOME/gsb-research-computing-ai-skills
source .venv/bin/activate
python scripts/chain_step2.py
