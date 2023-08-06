
import numpy as np

def sample_acf(ts, max_lag=None):
    """
    Computes the sample autocorrelation function of a time series.
    
    Parameters
    ----------
    ts : np.array
        The time series whose sample autocorrelation function is desired.
    
    Returns
    -------
    ac : np.array
        Array of autocorrelations at lags between 0 and max_lag.
        
    Notes
    -----
    The default value for max_lag is the length of the time series minus 1.
    """
    if max_lag is None:
        max_lag = len(ts) - 1
    if max_lag >= len(ts):
        raise ValueError("max_lag must be less than the length of the time "
                          "series.")
    n = len(ts); m = np.mean(ts)
    c = np.sum((ts - m) ** 2) / float(n)
    def r(h):
        return ((ts[:n-h]-m)*(ts[h:] - m)).sum()/(n*c)
    return np.array([r(i) for i 
                     in np.arange(n)][:max_lag+1])