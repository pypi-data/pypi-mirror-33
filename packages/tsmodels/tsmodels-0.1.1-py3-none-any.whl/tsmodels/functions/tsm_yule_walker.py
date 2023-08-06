
import numpy as np
from tsmodels.functions.tsm_sample_acvf import sample_acf

def yule_walker(ts, p):
    """
    Estimates the parameters of an AR(p) process using the Yule-Walker 
    estimators.
    
    Parameters
    ----------
    ts : np.array
        It is assumed x has been mean-corrected by subtracting the sample mean.
    p : int
        The order of the AR process.
        
    Returns
    -------
    pars : np.array
        The estimated AR parameters.
    """
    if p == 0:
        return np.array([])
    acs = sample_acf(ts, max_lag=p)
    m = yule_walker_matrix(acs[:-1])
    v = np.matrix(acs[1:].reshape(len(acs[1:]), 1))
    return np.array(np.linalg.inv(m)*v).flatten()

def yule_walker_matrix(v):
    """
    Creates a matrix for yule_walker function as well as 
    arma_mle functions.
    """
    n = len(v)
    if type(v) != "list":
        v = list(v)
    triu = []
    for i in range(n, 0, -1):
        triu += v[0:i]
    m = np.matrix(np.ones((n,n)))
    xs,ys = np.triu_indices(n,k=0)
    m[xs,ys] = triu; m[ys,xs] = triu
    return m