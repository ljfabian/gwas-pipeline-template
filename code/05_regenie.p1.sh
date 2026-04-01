#!/bin/bash
#SBATCH --job-name=05_regenie                       # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=16                                 # Run on a single CPU
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --mem=50gb                                  # Job memory request
#SBATCH --time=24:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job

# load modules..
module add apps/regenie

# load variables..
fileset=$1
pc_file=$2
pheno_file=$3
bsize=$4
output=$5
ld_in_file=$6

# add in threading according to number available on node
threads=$(nproc)

echo 'starting analysis on' $fileset

regenie \
    --step 1 \
    --pgen $fileset \
    --extract $ld_in_file \
    --covarFile $pc_file \
    --phenoFile $pheno_file \
    --threads $threads \
    --iid-only \
    --bt \
    --bsize $bsize \
    --out $output
 
head ${output}_pred.list