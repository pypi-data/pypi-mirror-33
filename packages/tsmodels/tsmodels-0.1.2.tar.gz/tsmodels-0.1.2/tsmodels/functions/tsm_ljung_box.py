
from tsmodels.functions.tsm_sample_acvf import sample_acf
import numpy as np
from scipy.stats import chi2

def ljung_box(ts, num_lags=20):
    """
    Performs a Ljung-Box test on ts. The null hypothesis is that the first 
    num_lags autocorrelations are 0.
    
    Parameters
    ----------
    ts : np.array
        The time series.
    num_lags : int
        The number of lags to test.
        
    Returns
    -------
    res : float
        p-value for the test.
    """
    n=len(ts)
    acf2 = (sample_acf(ts, num_lags)[1:])**2
    den = np.arange(n-1,n-num_lags-1, -1)
    q=n*(n+2)*np.sum(acf2/den)
    return 1.0-chi2.cdf(q, df=num_lags)
    