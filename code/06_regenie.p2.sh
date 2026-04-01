#!/bin/bash
#SBATCH --job-name=06_regenie                       # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=16                                 # Run on a single CPU
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --mem=100gb                                 # Job memory request
#SBATCH --time=36:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job


# load modules..
module add apps/regenie

# load variables..
fileset=$1
pc_file=$2
pheno_file=$3
bsize=$4
pred_file=$5
output=$6
p_threshold=$7

# add in threading according to number available on node
threads=$(nproc)

echo $threads

regenie \
    --step 2 \
    --pgen $fileset \
    --covarFile $pc_file \
    --phenoFile $pheno_file \
    --iid-only \
    --bt \
    --spa \
    --threads $threads \
    --pThresh $p_threshold \
    --pred $pred_file \
    --bsize $bsize \
    --out $output

# --firth