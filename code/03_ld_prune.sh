#!/bin/bash
#SBATCH --job-name=03_ld_prune                      # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=1                                  # Run on a single CPU
#SBATCH --mem=20gb                                  # Job memory request
#SBATCH --time=02:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job

# load variables in..
input=$1

# LD var loading
ld_window_size=$2
ld_step_size=$3
ld_threshold=$4
ld_prune_out=$5

high_ld_region=$6
relatedness_keep=$7

# load module..
module add apps/plink2

# prune the file
plink2 \
    --pfile $input \
    --exclude range $high_ld_region \
    --keep $relatedness_keep \
    --indep-pairwise $ld_window_size $ld_step_size $ld_threshold \
    --out $ld_prune_out
