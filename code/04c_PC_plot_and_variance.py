import numpy as np
import pandas as pd
import sys
import plotly.express as px
import plotly.io as pio
from kaleido import write_fig_sync
# from snakemake.script import snakemake

# define log paths to write to
sys.stdout = open(snakemake.log["log"], "w")
sys.stderr = open(snakemake.log["err"], "w")

eigenval = np.loadtxt(snakemake.input[1])
eigenvec = pd.read_csv(snakemake.input[0], sep='\t')
original_eigenvec = pd.read_csv(snakemake.input[2], sep='\t')

total_pcs = snakemake.params.total_pcs
output_dir = snakemake.params.output_path
output_image= snakemake.output

### Calculate variance explained
# Explained variance ratio
explained_variance_ratio = eigenval / np.sum(eigenval)

# Cumulative variance
cumulative_variance = np.cumsum(explained_variance_ratio)

print('Explained variances:')

# Print results
for i, (evr, cum) in enumerate(zip(explained_variance_ratio, cumulative_variance), 1):
    print(f"PC{i}: {evr:.4f} (Cumulative: {cum:.4f})")
    
### plot PCs
cols = ["FID", "IID"] + [f"PC{i}" for i in range(1, int(total_pcs)+1)]  # assuming up to 20 PCs

eigenvec["re-calculated_PCs"] = True
original_eigenvec["original_calculated_PCs"] = True

print(original_eigenvec, eigenvec)

# Due to merging left to new calculated ones, this will automatically exclude outliers, which were previously identified and excluded in the PC formatting steps. These do not get joined in. Merging will identify those with origianl PC values (not imputed/re-scored)
merged = eigenvec.merge(original_eigenvec[["#IID", 'original_calculated_PCs']], right_on="#IID", left_on='IID', how="left", indicator=True)

merged['group'] = ['Original' if i ==True else 'Calculated' for i in merged['original_calculated_PCs']]

print(merged)
# merged.to_csv('merged_pcs.csv', sep='\t')

def plot_pcs(df, output, grouping=False, total_pcs=total_pcs):
    features = [f"PC{i}" for i in range (1, total_pcs+1)]

    # if grouping add colour differentiation
    if grouping:
        fig = px.scatter_matrix(
            df,
            dimensions=features,
            color=grouping,
            title=f'PCA plot'
        )

    # otherwise just plot as normal
    else:
        fig = px.scatter_matrix(df, dimensions=features, title=f"PCA plot")
    fig.update_traces(diagonal_visible=False)

    write_fig_sync(
        fig, f"{output}", opts={"width": 1200, "height": 1200, "scale": 2}
    )

plot_pcs(merged, output_image, grouping='group')
