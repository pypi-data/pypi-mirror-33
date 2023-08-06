
import numpy as np
from tsmodels.functions.tsm_yule_walker import yule_walker
from tsmodels.functions.tsm_arma_obj_funs import arma_css
from tsmodels.classes.tsm_LinearModel import LinearModel

def hannan_rissanen(ts, p, q):
    """
    Used to compute Hannan Rissanen estimates of an ARMA(p, q) model.
    
    Parameters
    ----------
    ts : np.array
        Contains the time series values.
    p : int
        Represents the AR order.
    q : int
        Represents the MA order.
        
    Returns
    -------
    pars : np.array
        Estimated parameters of the ARMA process. Has the form np.array([mu, 
        phi_1, ... phi_p, theta_1, ... theta_q, sigma])
        
    Notes
    -----
    The initial number of AR terms fit (as in ITSM) is 20+p+q.
    """
    mean = np.mean(ts)
    ts = ts - mean
    m = 20+p+q; n = len(ts)
    # fit a high order AR process to the data
    yw_pars = yule_walker(ts, m)
    sto = np.empty((n, 2))*np.nan
    sto[:, 0] = ts
    for i in range(m, n):
        sto[i, 1] = (sto[i, 0] - np.dot(yw_pars, np.flipud(sto[i-m:i, 0])))
    x, y = hannan_rissanen_dm(sto, p, q)
    hres = LinearModel(x, y).pars
    mu = mean*(1 - np.sum(hres[:p]))
    hres = np.concatenate([[mu], hres])
    sigma = np.sqrt(arma_css(hres, ts, {"order":[p,q]})/(n-m-q))
    return np.concatenate([hres, [sigma]])

def hannan_rissanen_dm(ts, p, q):
    """
    Creates a design matrix for hannan_rissanen function.
    
    Parameters
    ----------
    ts : np.array
        Should contain the time series in column 0 and 
        errors in column 1.
    p : int
        Order of AR process.
    q : int
        Order of MA process.
        
    Returns
    -------
    x, y : np.matrix
        A design matrix and response vector for OLS regression.
    """
    n = ts.shape[0]
    tmp_0 = np.argwhere(np.isnan(ts[:,0]))
    start_0 = tmp_0.max() + 1 if len(tmp_0) != 0 else 0
    tmp_1 = np.argwhere(np.isnan(ts[:,1]))
    start_1 = tmp_1.max() + 1 if len(tmp_1) != 0 else 0
    start = max(start_0 + p, start_1 + q)
    num_rows = n - start
    if num_rows > 0:
        dm = np.zeros((num_rows, p + q))
        for i in range(0, num_rows):
            ar = np.flipud(ts[i+start-p:i+start,0])
            ma = np.flipud(ts[i+start-q:i+start,1])
            dm[i,] = np.concatenate([ar, ma])
        return (np.matrix(dm), 
                np.matrix(ts[start:n, 0].reshape((n-start, 1))))
    else:
        raise ValueError("Not enough data for estimation.")