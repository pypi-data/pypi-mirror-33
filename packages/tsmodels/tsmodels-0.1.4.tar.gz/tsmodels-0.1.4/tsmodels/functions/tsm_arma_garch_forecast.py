
import numpy as np
from tsmodels.functions.tsm_densities import q_std_norm, q_std_ged, q_std_t
from tsmodels.functions.tsm_innov_alg import innov_alg_preds
from tsmodels.functions.tsm_arma_acvf import arma_vcm

def arma_garch_forecast(ts, pars, innov_dist, h=1, static_index=None, 
                        indices=None, conf_level=0.95, sto=None):
    """
    This function computes the h-step ahead best linear predictions for 
    each index in indices.
    
    Parameters
    ----------
    ts : np.array
        The time series to compute predictions for.
    pars : dict
        May have "mu", "phi", "theta", "omega", "alpha", "beta" and "shape" as 
        keys with ints or numpy arrays as values.
    innov_dist : str
        The distribution of the innovations.
    static_index : int or None
        If an index is given, static predictions are made using all information 
        up to and including this index; if None, rolling predictions are made.
    h : int
        If making rolling predictions, ts[k] is predicted using all information 
        up to and including ts[k-h].
    indices : np.array
        The indices to predict. Defaults to all the indices in ts if making 
        rolling predictions.
    conf_level : float
        The computed prediction intervals will contain the true values
        will probability equal to conf_level.

    Returns
    -------
    pred : np.array
        The predictions.
        
    Notes
    -----
    If predictions have to be made more than one step ahead, a bootstrap is  
    used to compute prediction intervals.
    """
    n = len(ts)
    mu = pars["mu"]; phi = pars["phi"]; shape = pars["shape"]
    theta = pars["theta"]; omega = pars["omega"]
    alpha = pars["alpha"]; beta = pars["beta"]
    p=len(phi); q=len(theta); m=len(alpha); s=len(beta)
    k=max(q, m, s); g=max(q, m); l=max(p, k)
    rolling = static_index is None
    indices = np.sort(indices)
    N = len(indices)        
    max_index = indices[-1]
    if rolling:
        if max_index >= n+h:
            raise ValueError("The maximum index to be predicted must be less "
                             "than len(ts) + h.")
    # set quantile function
    if innov_dist == "norm":
        quantile = q_std_norm
    if innov_dist == "ged":
        quantile = lambda x : q_std_ged(x, shape)
    if innov_dist == "t":
        quantile = lambda x : q_std_t(x, shape)
    # initialise storage array
    ext = max(k-p, 0)
    sto = np.empty((max_index+1+ext, 4))*np.nan
    # fill in observed values
    if n-1 >= max_index:
        sto[ext:ext+max_index+1,0] = ts[0:max_index+1]
    else:
        sto[ext:ext+n,0] = ts
    # set starting value for residuals
    sto[p+ext-g:p+ext, 1] = 0
    # set starting value for conditional vars
    sto[p+ext-s:p+ext, 2] = omega/(1.0 - np.sum(alpha) - np.sum(beta))
    # set quantiles
    lq = (1.0-conf_level)/2.0; uq = 1.0 - lq 
    for i in range(p+ext, max_index+1+ext):
        if i < n + ext:
            # fill in residual
            sto[i, 1] = (sto[i, 0] - mu - np.dot(phi, sto[i-p:i, 0][::-1]) - 
               np.dot(theta, sto[i-q:i, 1][::-1]))
        # fill in conditional var
        sto[i, 2] = (omega + np.dot(alpha, (sto[i-m:i, 1]**2)[::-1]) + 
           np.dot(beta, sto[i-s:i, 2][::-1]))
        # fill in one-step ahead prediction
        sto[i, 3] = sto[i, 0] - sto[i, 1]
    if rolling and h==1:
        # store one-step ahead upper and lower prediction bounds
        osa_upper_bounds = sto[:,3] + quantile(uq)*np.sqrt(sto[:,2])
        osa_lower_bounds = sto[:,3] + quantile(lq)*np.sqrt(sto[:,2])
        return {"preds":sto[indices+ext,3], "upper_bounds":
            osa_upper_bounds[indices+ext], "lower_bounds":
                osa_lower_bounds[indices+ext]}
    else:
        # set number of bootstraps
        B = 20000
        # first consider static predictions
        # I should include a function here to do h-step rolling
        # preds using static prediction code.
        if not rolling:
            # compute the number of resids to draw
            e = max_index-static_index
            # extract the residuals to sample from
            # what indices should we create res_pool from?
            # static_index must be greater than p
            res_pool = sto[p+ext:static_index+ext+1,1]/np.sqrt(sto
                          [p+ext:static_index+ext+1,2])
            sims = np.empty((B, e))*np.nan
            for i in range(0, B):
                resids = np.random.choice(res_pool, e)
                #print("resids", resids)
                # static_index+1 since this is the first index we are
                # predicting for
                sto2 = np.copy(sto[static_index+1-l:static_index+1, 0:3])
                sto2 = np.vstack([sto2, np.empty((e,3))*np.nan])
                #print("sto2 init:", sto2)
                for j in range(0, e):
                    # first fill in conditional variance
                    sto2[l+j,2] = omega + np.dot(alpha, sto2[l+j-m:l+j,1]
                    [::-1]**2) + np.dot(beta, sto2[l+j-s:l+j,2][::-1])
                    # then fill in residual
                    sto2[l+j,1] = resids[j]*np.sqrt(sto2[l+j,2])
                    # then fill in simulated value
                    sto2[l+j,0] = (mu + np.dot(phi, sto2[l+j-p:l+j,0][::-1]) + 
                        np.dot(theta, sto2[l+j-q:l+j,1][::-1]) + sto2[l+j,1])
                    #print("sto2:", sto2)
                sims[i,:] = sto2[l:,0]
                #print("sims:", sims)
            upper_bounds = np.percentile(sims, uq*100.0, 0)
            lower_bounds = np.percentile(sims, lq*100.0, 0)
            arma_mean = mu/(1.0-np.sum(phi))
            # it doesn't matter what value of sigma we use below
            vcm = arma_vcm(phi, theta, max_index+1, 1.0)
            preds = (innov_alg_preds(ts, vcm, h, static_index, indices)
            ["preds"]+arma_mean)
            upper_bounds = upper_bounds[indices-static_index-1]
            lower_bounds = lower_bounds[indices-static_index-1]
        else:
            preds = np.zeros(N)
            upper_bounds = np.zeros(N); lower_bounds = np.zeros(N)
            for i, q in enumerate(indices):
                res = arma_garch_forecast(ts=ts, pars=pars, 
                                           innov_dist=innov_dist, h=h, 
                                           static_index=q-h, 
                                           indices=np.array([q]), 
                                           conf_level=conf_level)
                preds[i] = res["preds"][0]
                upper_bounds[i] = res["upper_bounds"][0]
                lower_bounds[i] = res["lower_bounds"][0]
    return {"preds":preds, "upper_bounds":upper_bounds, "lower_bounds":
                lower_bounds}