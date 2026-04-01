import numpy as np
import pandas as pd
import sys
from scipy.stats import chi2
# from snakemake.script import snakemake

# define log paths to write to
sys.stdout = open(snakemake.log["log"], "w")
sys.stderr = open(snakemake.log["err"], "w")

# Inputs - should be read directly from snakefile due to 'script' call method.
sscore_file = snakemake.input[0]
eigenval_file = snakemake.params.eigenval
eigenvec_file = snakemake.params.eigenvec
output_eigenvec_file = snakemake.output[0]
output_eigenval_file = snakemake.output[1]

output_covars_file = snakemake.output[2]

# ensure you are only using the PCs which you sepcified
max_pcs = snakemake.params.pc_count
pc_cols = [f'PC{i}' for i in range(1, max_pcs+1)]

# Load projected scores
sscore = pd.read_csv(sscore_file, sep='\s+')

print('sscores:\n', sscore)

# Load eigenvalues and compute sqrt
eigenvals = np.round(np.loadtxt(eigenval_file), 5)
print(eigenvals)
sqrt_eigenvals = np.sqrt(eigenvals)

# Extract SCORE columns and rescale
score_cols = [col for col in sscore.columns if col.startswith("PC")]
pcs = sscore[score_cols].values
pcs_scaled = np.round(pcs / (-sqrt_eigenvals[: pcs.shape[1]]/2), 8)

print("pcs_scaled\n", pcs_scaled)

# Construct new .eigenvec-style DataFrame
out_df = sscore[["#IID"]].copy()
out_df.rename(columns={"#IID": "FID"}, inplace=True)
out_df['IID'] = out_df['FID']

# to get sscores back to the eigenvec values, use = sscore / (-sqrt(eigenval)/2)
# From: https://groups.google.com/g/plink2-users/c/W6DL5-hs_Q4
# example tested
for i in range(pcs_scaled.shape[1]):
    out_df[f"PC{i+1}"] = pcs_scaled[:, i]

# if needed, exclude outliers calculated by mahalanobis distance
if snakemake.params.exclude_outliers:
    outlier_df = out_df
    
    X_base = outlier_df[pc_cols].values # only calculate outliers on first 5 PCs, otherwise its 2/3k individuals?!
    
    mean_vec = np.mean(X_base, axis=0)
    cov_matrix = np.cov(X_base, rowvar=False)
    inv_cov_matrix = np.linalg.pinv(cov_matrix)

    # X_all = outlier_df[pc_cols].values
    diff = X_base - mean_vec
    mahal_sq = np.sum(diff @ inv_cov_matrix * diff, axis=1)
    
    outlier_df['mahal_sq'] = mahal_sq
    
    alpha = 0.001
    threshold = chi2.ppf(1 - alpha, len(pc_cols))
    outlier_df["outlier"] = outlier_df["mahal_sq"] > threshold

    print(f"Outliers detected: {outlier_df['outlier'].sum()}")
    outliers = outlier_df[outlier_df['outlier'] == True]['IID']

    out_df = out_df[~out_df['IID'].isin(outliers)]

covar_cols = ['FID', 'IID'] + pc_cols
covar_df = out_df[covar_cols]

# save eigenvec
print(f"Saving scaled PCs to: {output_eigenvec_file}")
out_df.to_csv(output_eigenvec_file, sep="\t", index=False)

# merge in covar file if provided
if snakemake.params.covar_file:
    covars = pd.read_csv(snakemake.params.covar_file)
    covars = covars[['alnqlet', 'age']]
    covars.rename(columns={'alnqlet': 'IID'}, inplace=True)
    covar_df = pd.merge(covar_df, covars, on='IID', how='left')
    print(f'Saving covar file for regenie to:', output_covars_file)

    covar_df.to_csv(output_covars_file, sep="\t", index=False)


# save eigenval (same but new name convention for ease)
print(f'Saving eigenvalues to:', output_eigenval_file)
np.savetxt(output_eigenval_file, eigenvals, fmt="%.5f")
