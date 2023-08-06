
import numpy as np
from tsmodels.functions.tsm_arma_to_ma import arma_to_ma
from tsmodels.functions.tsm_yule_walker import yule_walker_matrix

def arma_vcm(ar, ma, n, sigma):
    """
    This function computes the theoretical variance-covariance matrix of a
    given ARMA process.
    
    Parameters
    ----------
    ar : np.array
        Contains the AR parameters of the model.
    ma : np.array
        Contains the MA parameters of the model.
    n : int
        An array with shape (n, n) is produced. 
    sigma : float
        The standard deviation of the errors.
        
    Returns
    -------
    vcm : np.array
        The theoretical variance-covariance matrix of the process.
    """  
    return yule_walker_matrix(arma_acvf(ar, ma, n-1, sigma))

def arma_acvf(ar, ma, max_lag, sigma):
    """
    This function computes a theoretical ACVF for an ARMA process.
    
    Parameters
    ----------
    ar : np.array
        Contains the AR parameters of the model.
    ma : np.array
        Contains the MA parameters of the model.
    max_lag : int
        The maximum ACVF lag to compute.
    sigma : float
        The standard deviation of the errors.
        
    Returns
    -------
    acvf : np.array
        The theoretical ACVF of the process up to max_lag.
    """
    p = len(ar); q = len(ma)
    sto = np.zeros((p+1, 2*p+1))
    for i in range(0, p+1):
        sto[i, i:i+p+1] = np.concatenate([[1], -ar])
    sto[:,0:p] = (sto[:,0:p] + 
       np.flip(sto[:,(p+1):(2*p+1)], axis=1))
    sto = np.fliplr(np.flipud(sto[:, 0:(p+1)]))
    psi = arma_to_ma(ar, ma, q)
    ma = np.concatenate([[1], ma])
    rhs = np.zeros((max_lag+1, 1))
    for i in range(0, max_lag+1):
        if i < q+1:
            rhs[i,0] = sigma**2*np.dot(ma[i:q+1], psi[0:q+1-i])
        else:
            rhs[i,0] = 0
    acvf = np.matmul(np.linalg.inv(sto), rhs[0:p+1,0]).flatten()
    if max_lag <= p:
        return acvf[0:max_lag+1]
    else:
        acvf = np.concatenate([acvf, [np.nan]*(max_lag - p)])
        for i in range(p+1, max_lag+1):
            acvf[i] = np.dot(ar, np.flipud(acvf[i-p:i])) + rhs[i,0]
    return acvf

def arma_acf(ar, ma, max_lag):
    """
    This function computes the theoretical ACF of an ARMA process.
    
    Parameters
    ----------
    ar : np.array
        Contains the AR parameters of the model.
    ma : np.array
        Contains the MA parameters of the model.
    max.lag : int
        The maximum ACVF lag to compute.
        
    Returns
    -------
    acf : np.array
        The theoretical ACF of the process up to max_lag.
    """
    acvf = arma_acvf(ar, ma, max_lag, 1)
    return acvf/float(acvf[0])