
import matplotlib.pyplot as plt
import numpy as np
from tsmodels.functions.tsm_sample_acvf import sample_acf
from tsmodels.settings.tsm_settings import figsize

def plot_acf(ts, max_lag=None):
    """
    Plots the ACF of ts.
    
    Parameters
    ----------
    ts : np.array
        The time series.
    max_lag : int
        The maximum lag which the ACF will be plotted up to.
        
    Returns
    -------
    ax : matplotlib.axes
        A plot of the ACF.
        
    Notes
    -----
    We also plot standard errors for the autocorrelations, assuming that ts 
    is a white noise sequence.
    
    References
    ----------
    Shumway, R. & Stoffer, D. (2017). Time Series Analysis and Its 
    Applications : With R Examples. Cham, Switzerland: Springer.
    """
    n = len(ts)
    error = 1.96*n**(-0.5)
    if max_lag is None:
        max_lag = len(ts) - 1
    acf = sample_acf(ts, max_lag)
    x = np.arange(0, max_lag + 1)
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x, acf, width=0, linewidth=2, edgecolor="#0038A8")
    ax.axhline(color="black")
    ax.axhline(error, color="black", alpha=0.8, linestyle="dashed")
    ax.axhline(-error, color="black", alpha=0.8, linestyle="dashed")
    if max_lag <= 20:
        ax.set_xticks(x)
    ax.set_xlabel("Lag")
    ax.set_ylabel("ACF")    
    return ax