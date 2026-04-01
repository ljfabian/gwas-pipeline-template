#!/bin/bash
#SBATCH --job-name=02_pc_filter                     # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=4                                  # Run on a single CPU
#SBATCH --mem=20gb                                  # Job memory request
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --time=04:00:00                             # Time limit hrs:min:sec
#SBATCH --account=your_account                      # account used for the job

# load variables in..
input=$1
output=$2

# filter criteria - defined in snakemake
r2=$3
maf=$4
king_cutoff=$5
king_location=$6
geno=$7
mind=$8
hwe=$9

# typed snps extracted from original vcfs:
typed_snps=${10}
# load modules..
module add apps/plink2

# filter on maf and r2
echo '-----FILTER ON MAF AND R2-----'
plink2 \
    --pfile $input \
    --exclude-if-info "R2<${r2}" \
    --extract $typed_snps \
    --maf $maf \
    --make-pgen \
    --out ${output}_mafr2

echo 'filtering on maf and r2 leaves:'
wc -l ${output}_mafr2.pvar

# make relatedness file for exclusion if needed...
echo '-----MAKE RELATEDNESS TABLE-----'
plink2 \
    --pfile ${output}_mafr2 \
    --make-king-table \
    --king-cutoff $king_cutoff \
    --out $king_location

# perform the general filtering required
echo '-----ADDITIONAL QC FOR PC-----'
plink2 \
    --pfile ${output}_mafr2 \
    --maf $maf \
    --geno $geno \
    --mind $mind \
    --hwe $hwe \
    --make-pgen \
    --out $output

echo 'number of snps filtered to:'
wc -l $output.pvar

# clean up
if [[ -e "$output.psam" ]]; do
    rm ${output}_mafr2.*
fi