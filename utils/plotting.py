import pandas as pd
import plotly.graph_objects as go
import numpy as np


def experiment_summary_frame(experiment_results):
    """
    Mean results for each performance measure by experiment

    Parameters:
    ----------
    experiment_results: dict
        dictionary of replications.
        Key identifies the performance measure

    Returns:
    -------
    pd.DataFrame
    """
    columns = []
    summary = pd.DataFrame()
    for sc_name, replications in experiment_results.items():
        summary = pd.concat([summary, replications.mean()], axis=1)
        columns.append(sc_name)

    summary.columns = columns
    return summary


def get_plotly_hists(data_df):
    hists = {}
    for col in data_df.select_dtypes(include=np.number).columns:
        data = data_df[col]
        mean = data.mean()
        std = data.std()
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x = data, 
            nbinsx = int(np.ceil(np.log2(len(data_df))+1))
        ))
        fig.add_vline(x=mean, line_width=2, line_color="white")
        # fig.add_vline(x=mean-std, line_width=1, line_dash="dash", line_color="gray")
        # fig.add_vline(x=mean+std, line_width=1, line_dash="dash", line_color="gray")
        fig.update_layout(
            title = f"{col} distribution | mean = {mean:.2f}, std = {std:.2f}",
            xaxis_title = col,
            yaxis_title = "Count",
        )
        hists[col] = fig
    return hists



