
import numpy as np
from tsmodels.functions.tsm_yule_walker import yule_walker_matrix
from tsmodels.functions.tsm_innov_alg import innov_alg_preds
from tsmodels.functions.tsm_densities import d_mult_norm
from tsmodels.functions.tsm_arma_acvf import arma_acvf
    
def arma_css(pars, vals, mean_model):
    """
    Used to compute the conditional sum of squares of an arma model, given 
    pars.
    
    Parameters
    ----------
    pars : np.array
        Should take the form np.array([mu, phi_1, ... phi_p, theta_1, ... 
        theta_q]).
    vals : np.array
        Contains the time series values.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
        
    Notes
    -----
    Currently we only allow for normal errors.
    """
    n = len(vals)
    p, q = mean_model["order"]
    k = max(p, q)
    mu = pars[0]; 
    phi = pars[1:p+1]; theta = pars[p+1:p+q+1]
    # initialise storage array
    sto = np.empty((n, 2))*np.nan
    sto[:, 0] = vals
    # set starting value for residuals
    sto[0:k, 1] = 0
    # fill in residuals
    for i in range(k, n):
        # must reverse values in sto
        sto[i, 1] = (sto[i, 0] - mu - np.dot(phi, np.flipud(sto[i-p:i, 0])) - 
           np.dot(theta, np.flipud(sto[i-q:i, 1])))
    # it doesn't matter whether we return np.sum(sto[:, 1]**2) or 
    # np.sum(sto[k:, 1]**2) since first k residuals are 0
    return np.sum(sto[:, 1]**2)   

def arma_mle_a(pars, vals, mean_model):
    """
    Computes the negative log-likelihood of an arma model by computing the 
    inverse of the autocovariance matrix.
    
    Parameters
    ----------
    pars : np.array
        Should take the form np.array([mu, phi_1, ... phi_p, theta_1, ... 
        theta_q, sigma]).
    vals : np.array
        Contains the time series values.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
        
    Notes
    -----
    Currently we only allow for normal errors.
    """
    n = len(vals)
    p, q = mean_model["order"]
    mu = pars[0]; sigma = pars[p+q+1]
    phi = pars[1:p+1]; theta = pars[p+1:p+q+1]
    vals = np.matrix((vals - mu/(1.0 - np.sum(phi))).reshape((len(vals), 1)))
    # create autocovariance matrix
    acvm = yule_walker_matrix(arma_acvf(phi, theta, n-1, sigma))
    return -np.log(d_mult_norm(vals, 0, acvm))    
            
def arma_mle_b(pars, vals, mean_model):
    """
    Computes the negative log-likelihood of an arma model using the innovations 
    algorithm.
    
    Parameters
    ----------
    pars : np.array
        Should take the form np.array([mu, phi_1, ... phi_p, theta_1, ... 
        theta_q, sigma]).
    vals : np.array
        Contains the time series values.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
        
    Notes
    -----
    Currently we only allow for normal errors. 
    """
    n = len(vals)
    p, q = mean_model["order"]
    mu = pars[0]; sigma = pars[p+q+1]
    phi = pars[1:p+1]; theta = pars[p+1:p+q+1]
    vals = vals - mu/(1.0 - np.sum(phi))
    vcm = yule_walker_matrix(arma_acvf(phi, theta, n, sigma))
    osa = innov_alg_preds(vals, vcm, indices=np.arange(0,n))
    return (n/2.0*np.log(2*np.pi) + 0.5*np.sum(np.log(osa["sigma2"])) + 
            0.5*np.sum((vals-osa["preds"])**2/osa["sigma2"]))