
import numpy as np
from scipy.special import gamma, beta
from scipy.stats import norm, gennorm, t

def d_std_norm(x):
    """
    Computes the density of a standard normal distribution.
    
    Parameters
    ----------
    x : float
        The value at which the density is to be computed.
    """
    return norm.pdf(x)

def q_std_norm(p):
    """
    Computes the quantile of a standard normal distribution.
    
    Parameters
    ----------
    p : float
        A probability.
    """
    return norm.ppf(p)
    
def d_std_t(x, shape):
    """
    Computes the density of a standard t distribution.
    
    Parameters
    ----------
    x : float
        The value at which the density is to be computed.
    shape : float
        The shape parameter of the standard t distribution. Must be greater
        than 2.
    """
    scale = np.sqrt(shape/(shape-2.0))
    return t.pdf(x*scale, shape)*scale

def q_std_t(p, shape):
    """
    Computes the quantile of a standard t-distribution.
    
    Parameters
    ----------
    p : float
        A probability.
    shape : float
        The shape parameter of the standard t distribution. Must be greater
        than 2.
    """
    scale = np.sqrt(shape/(shape-2.0))
    return t.ppf(p, shape)/scale
   
def d_std_ged(x, shape):
    """
    Computes the density of a standard GED distribution.
    
    Parameters
    ----------
    x : float
        The value at which the density is to be computed.
    shape : float
        The shape parameter of the standard GED distribution. Must be greater 
        than 0.
    """
    scale = np.sqrt(gamma(3.0/shape)/gamma(1.0/shape))
    return gennorm.pdf(x*scale, shape)*scale

def q_std_ged(p, shape):
    """
    Computes the quantile of a standard GED distribution.
    
    Parameters
    ----------
    p : float
        A probability.
    shape : float
        The shape parameter of the standard GED distribution. Must be greater 
        than 0.
    """
    scale = np.sqrt(gamma(3.0/shape)/gamma(1.0/shape))
    return gennorm.ppf(p, shape)/scale
    
def d_mult_norm(vals, mu, vcm):
    """
    Computes the density of a multivariate normal distribution.
    
    Parameters
    ----------
    vals : np.matrix
        Must have shape (n, 1).
    mu : np.matrix or int
        If matrix, must have shape (n, 1).
    vcm : np.matrix
        The variance-covariance matrix of the random variables. Must have shape 
        (n, n).
    """
    n = len(vals)
    inv = np.linalg.inv(vcm)
    det = np.linalg.det(vcm)
    return ((2*np.pi)**(-n/2.0)*det**(-0.5)*np.exp(-0.5*np.transpose(vals - 
            mu)*inv*(vals - mu)))[0,0] 