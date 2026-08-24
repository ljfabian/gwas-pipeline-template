import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats


def load_regenie(file):
    df = pd.read_csv(file, sep=None, engine="python")
    
    required_cols = [
        "CHROM", "GENPOS", "ID",
        "ALLELE0", "ALLELE1",
        "A1FREQ", "N", "TEST",
        "BETA", "SE", "CHISQ",
        "LOG10P", "EXTRA"
    ]
    
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    df = df.copy()
    
    # Remove NA or invalid LOG10P
    df = df[df["LOG10P"].notna()]
    df = df[df["LOG10P"] >= 0]
    
    # Find minimum N
    print('min N:', df['N'].min())
    print('max N:', df['N'].max())


    # Convert chromosome labels
    df["CHROM"] = df["CHROM"].astype(str)
    df["CHROM"] = df["CHROM"].replace({"X": "23", "Y": "24", "MT": "25"})
    df["CHROM"] = df["CHROM"].astype(int)
    
    # Compute p-value safely
    df["P"] = 10 ** (-df["LOG10P"])
    
    return df


def qq_plot(df, save_name, max_points=200_000, keep_top=5000):
    pvals = np.sort(df["P"].values)
    n = len(pvals)

    expected = -np.log10(np.arange(1, n + 1) / (n + 1))
    observed = -np.log10(pvals)

    if n > max_points:
        idx_top = np.arange(keep_top)
        n_rest_keep = max_points - keep_top
        log_idx = np.unique(np.geomspace(keep_top, n - 1, n_rest_keep).astype(int))
        idx = np.unique(np.concatenate([idx_top, log_idx]))
    else:
        idx = np.arange(n)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=expected[idx],
        y=observed[idx],
        mode="markers",
        marker=dict(size=4),
        name="Observed"
    ))

    maxval = max(expected.max(), observed.max())
    fig.add_trace(go.Scatter(
        x=[0, maxval], y=[0, maxval],
        mode="lines", name="Expected", line=dict(dash="dash")
    ))

    fig.update_layout(
        title="QQ Plot",
        xaxis_title="Expected -log10(P)",
        yaxis_title="Observed -log10(P)",
        template="simple_white"
    )
    fig.write_image(f"{save_name}.png", width=900, height=700, scale=1, engine='kaleido')


def calc_lambda(df):

    # calc lambda
    lambda_gc = df["CHISQ"].median() / stats.chi2.ppf(0.5, df=1)
    print(f"Genomic inflation factor (λGC): {lambda_gc:.4f}")

   
def manhattan_plot(df, genomewide_line, suggestive_line, save_name, max_points_per_chrom=50_000):
    df = df.sort_values(["CHROM", "GENPOS"]).copy()
    df["-log10P"] = df["LOG10P"]

    chrom_max = df.groupby("CHROM")["GENPOS"].max().reset_index()
    chrom_max["offset"] = chrom_max["GENPOS"].cumsum() - chrom_max["GENPOS"]
    df = df.merge(chrom_max[["CHROM", "offset"]], on="CHROM")
    df["BP_cum"] = df["GENPOS"] + df["offset"]

    chrom_centers = df.groupby("CHROM")["BP_cum"].median().reset_index()
    sugg_thresh = -np.log10(suggestive_line)

    fig = go.Figure()
    colors = ["#4C78A8", "#F58518"]

    for i, (chrom, group) in enumerate(df.groupby("CHROM")):
        sig = group[group["-log10P"] >= sugg_thresh]
        bulk = group[group["-log10P"] < sugg_thresh]
        if len(bulk) > max_points_per_chrom:
            bulk = bulk.sample(max_points_per_chrom, random_state=0)
        plot_group = pd.concat([sig, bulk])

        fig.add_trace(go.Scatter(
            x=plot_group["BP_cum"],
            y=plot_group["-log10P"],
            mode="markers",
            marker=dict(size=4, color=colors[i % 2]),
            name=f"Chr {chrom}"
        ))

    fig.add_hline(y=-np.log10(genomewide_line), line_dash="dash", line_color="red")
    fig.add_hline(y=-np.log10(suggestive_line), line_dash="dot", line_color="gray")

    fig.update_layout(
        title="Manhattan Plot (Regenie Step 2)",
        xaxis=dict(
            title="Chromosome",
            tickmode="array",
            tickvals=chrom_centers["BP_cum"],
            ticktext=chrom_centers["CHROM"]
        ),
        yaxis_title="-log10(P)",
        template="simple_white",
        showlegend=False
    )
    fig.write_image(f"{save_name}.png", width=1200, height=700, scale=2, engine='kaleido')


def main():
    
    # config
    genomewide_line = 5e-8
    suggestive_line = 1e-5

    path = "" # path to phenotype files
    print('----------------------')
    print(path)
    path_name = path.split('/')[-1]
    print(path_name)

    phenos = [
        # add in names of the phenotype files
    ]
    for pheno in phenos:
        
        print('-=-=-=-')
        print(pheno)

        regenie_file = f"{path}/{pheno}.regenie"

        # load data
        df = load_regenie(regenie_file)

        # genomic lambda
        calc_lambda(df)

        # plots
        print('generating plots.')
        qq_plot(df, f"qq_{pheno}")
        manhattan_plot(df, genomewide_line, suggestive_line, f"{path_name}-manhattan_{pheno}")
        print('plots generated.')

    print('finished.')

    
if __name__=='__main__':
    main()
