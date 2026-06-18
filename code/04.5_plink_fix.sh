#!/bin/bash
#SBATCH --job-name=04.5_pf                          # Job name
#SBATCH --mail-type=END,FAIL                        # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --ntasks=4                                  # Run on a single CPU
#SBATCH --mem=8gb                                   # Job memory request
#SBATCH --n-tasks-per-node=4                        # number of tasks running per node
#SBATCH --cpus-per-task=12                          # number of cpus per task
#SBATCH --time=01:00:00                             # Time limit hrs:min:sec
#SBATCH --account=youraccount                       # account used for the job

temp_path=$1
filtered_prefix=$2
gwas_prefix=$3


# run for subset version, which is used in regenie step 1
if head -1 "$temp_path/$filtered_prefix.psam" | grep -q '^#FID'; then
    
    # already has FID + IID and leave as is
    cp $temp_path/$filtered_prefix.psam $temp_path/pf_$filtered_prefix.psam

else
    
    # only #IID present, fix only #iid to iid fid with plink2
    sed '1s/^#IID/#FID\tIID/' $temp_path/$filtered_prefix.psam | \
    awk 'NR>1{print $1 "\t" $0; next}1' \
    > $temp_path/pf_$filtered_prefix.psam
fi
# copy pvar and pgen
cp $temp_path/$filtered_prefix.pvar $temp_path/pf_$filtered_prefix.pvar
cp $temp_path/$filtered_prefix.pgen $temp_path/pf_$filtered_prefix.pgen

# run for full version, used in regenie step 2
if head -1 "$temp_path/$gwas_prefix.psam" | grep -q '^#FID'; then

    # already has FID _ IID and leave as is
    cp $temp_path/$gwas_prefix.psam $temp_path/pf_$gwas_prefix.psam

else

    sed '1s/^#IID/#FID\tIID/' $temp_path/$gwas_prefix.psam | \
    awk 'NR>1{print $1 "\t" $0; next}1' \
    > $temp_path/pf_$gwas_prefix.psam

fi
# copy across pvar and pgen
cp $temp_path/$gwas_prefix.pvar $temp_path/pf_$gwas_prefix.pvar
cp $temp_path/$gwas_prefix.pgen $temp_path/pf_$gwas_prefix.pgen

#list all out to check they're present
ls $temp_path/pf*
#   plink2 \
#     --pfile $temp_path/$gwas_prefix \
#     --double-id \
#     --make-pgen \
#   --out $temp_path/pf_$gwas_prefix