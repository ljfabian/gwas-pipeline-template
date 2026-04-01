#!/bin/bash
#SBATCH --job-name=04_generate_pcs                  # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=4                                  # Run on a single CPU
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --mem=100gb                                 # Job memory request
#SBATCH --time=72:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job

# load variables in..
input=$1
ld_prune_output=$2
relatedness_keep=$3
pc_number=$4
output=$5


# load module..
module add apps/plink2

# check prune output
echo 'head of prune file:'
head $ld_prune_output

echo 'pc count:'
echo $pc_number

# use available memory
echo 'total mem available:'
free -m | awk '/^Mem:/{printf("%.1fGb\n",$2/1000)}'

# fetch threads
threads=$(nproc)
echo 'threads: ' $threads

# run PCA
plink2 \
    --pfile $input \
    --keep $relatedness_keep \
    --extract ${ld_prune_output} \
    --threads $threads \
    --pca allele-wts $pc_number vcols=chrom,ref,alt \
    --freq counts \
    --out $output
