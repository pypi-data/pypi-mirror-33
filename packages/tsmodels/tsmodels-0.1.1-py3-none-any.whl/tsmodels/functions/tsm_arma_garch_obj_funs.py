
import numpy as np
from tsmodels.functions.tsm_densities import d_std_norm, d_std_t, d_std_ged

def arma_garch_llh(pars, vals, mean_model, variance_model):
    """
    Used to compute the negative conditional log-likelihood of an ARMA_GARCH 
    model.
    
    Parameters
    ----------
    pars : np.array
        Should take the form np.array([mu, phi_1, ... phi_p, theta_1, ... 
        theta_q, omega, alpha_1, ... alpha_m, beta_1, ..., beta_s, shape]).
    vals : np.array
        Contains the time series values.
    variance_model : dict
        A dictionary of the form {'order' : [m, s], 'innov_dist' : innov_dist}
        where innov_dist may be "norm", "ged" or "t".
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
        
    Returns
    -------
    llh : float
        The negative conditional log-likelihood.
        
    Notes
    -----
    In future version we should include other GARCH types.

    References
    ----------
    Francq, C. & Zakoian. (2010). GARCH models : structure, statistical 
    inference and financial applications. Chichester, West Sussex, U.K: John 
    Wiley and Sons.
    """
    n = len(vals); nl = 0
    p, q = mean_model["order"]; m, s = variance_model["order"]
    k = max(q, m, s); g = max(q, m)
    mu = pars[0]; omega = pars[p+q+1]
    phi = pars[1:p+1]; theta = pars[p+1:p+q+1]
    alpha = pars[p+q+2:p+q+m+2]; beta = pars[p+q+m+2:p+q+m+s+2]
    innov_dist = variance_model["innov_dist"]
    if innov_dist in ["ged", "t"]:
        shape = pars[p+q+m+s+2]
        if innov_dist == "ged":
            pdf = lambda x : d_std_ged(x, shape)
        if innov_dist == "t":
            pdf = lambda x : d_std_t(x, shape)
    if innov_dist == "norm":
        pdf = lambda x : d_std_norm(x)
    # initialise storage array
    ext = max(k-p, 0)
    sto = np.empty((n + ext, 3))*np.nan
    sto[ext:, 0] = vals
    # set starting value for residuals
    sto[p+ext-g:p+ext, 1] = 0
    # fill in residuals
    for i in range(p+ext, n+ext):
        # note the values in sto must be reversed
        sto[i, 1] = (sto[i, 0] - mu - np.dot(phi, sto[i-p:i, 0][::-1]) - 
           np.dot(theta, sto[i-q:i, 1][::-1]))
    # set starting value for conditional vars
    sto[p+ext-s:p+ext, 2] = (omega + (np.sum(alpha) + np.sum(beta))*
       np.mean(sto[p+ext-g:, 1]**2))
    # fill in conditional vars
    for i in range(p+ext, n+ext):
        # note the values in sto must be reversed
        sto[i, 2] = (omega + np.dot(alpha, (sto[i-m:i, 1]**2)[::-1]) + 
           np.dot(beta, sto[i-s:i, 2][::-1]))
    # compute negative llh
    for i in range(p+ext, n+ext):
        nl -= np.log(1/np.sqrt(sto[i, 2])*pdf(sto[i, 1]/
                     np.sqrt(sto[i, 2])))
    return nl