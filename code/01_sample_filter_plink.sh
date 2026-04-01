#!/bin/bash
#SBATCH --job-name=01_qc                            # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=4                                  # Run on a single CPU
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --mem=40gb                                  # Job memory request
#SBATCH --time=15:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job

# load in variables..
input_pfile=$1
output=$2
filter_list=$3

# load modules..
module add apps/plink2

echo $input_pfile

# QC the data
plink2 \
    --pfile $input_pfile \
    --keep $filter_list \
    --make-pgen \
    --out $output
