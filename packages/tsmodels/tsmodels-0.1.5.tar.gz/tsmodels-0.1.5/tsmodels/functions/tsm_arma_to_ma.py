
import numpy as np

def arma_to_ma(ar, ma, max_lag):
    """
    This function converts an ARMA process to an infinite MA process.
    
    Parameters
    ----------
    ar : np.array
        Contains the AR parameters of the model.
    ma : np.array
        Contains the MA parameters of the model.
    max.lag : int
        The maximum MA(inf) coefficient required.
        
    Returns
    -------
    psi : np.array
        Vector of coefficients.
        
    Notes
    -----
    We do not currently check whether the model is causal.
    """
    p = len(ar)
    psi = np.concatenate([np.repeat(0, p), np.repeat(np.nan, max_lag + 1)])
    ma = np.concatenate([[1], ma, np.repeat(0, max_lag + 1 - len(ma))])
    for i in range(0, max_lag+1):
        psi[p+i] = ma[i] + np.dot(ar, np.flipud(psi[i:p+i]))
    return psi[p:]