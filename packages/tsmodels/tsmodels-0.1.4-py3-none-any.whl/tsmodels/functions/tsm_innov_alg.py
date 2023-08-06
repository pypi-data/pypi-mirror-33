
import numpy as np

def innov_alg(vcm):
    """
    Computes the theta parameters required to compute the one-step ahead best 
    linear predictors of a time series with finite second order moments.
    
    Parameters
    ----------
    vcm : np.matrix
        The variance-covariance matrix of the data.
    
    Returns
    -------
    theta, ose : np.array
        The parameters are contained in theta and the prediction errors are 
        contained in ose.
    """
    n = vcm.shape[0]
    theta = np.empty((n-1, n-1))*np.nan
    ose = np.empty(n)*np.nan
    ose[0] = vcm[0,0]
    for i in range(0, n-1):
        for j in range(i, -1, -1):
            if i == j:
                ext = 0
            else:
                ext = np.sum(theta[i-j-1,0:i-j]* theta[i, j+1:i+1]*
                             ose[0:i-j][::-1])
            theta[i,j] = ose[i-j]**(-1)*(vcm[i+1,i-j] - ext)
        ose[i+1] = (vcm[i+1, i+1] - np.dot(theta[i, 0:i+1]**2, 
           ose[0:i+1][::-1]))
    return (theta, ose)

def innov_alg_preds(ts, vcm, h=1, static_index=None, indices=None):
    """
    This function computes the h-step ahead best linear predictions for each 
    index in indices.
    
    Parameters
    ----------
    ts : np.array
        The time series to compute predictions for.
    vcm : np.array
        The varaiance-covariance matrix of the observations. If k is the 
        highest index to be predicted, should have shape (k+1, k+1).
    static_index : int or None
        If an index is given, static predictions are made using all information 
        up to and including this index; if None, rolling predictions are made.
    h : int
        If making rolling predictions, ts[k] is predicted using all information 
        up to and including ts[k-h].
    indices : np.array
        The indices to predict. Defaults to all the indices in ts if making 
        rolling predictions.
        
    Returns
    -------
    pred : np.array
        The h-step ahead predictions.
    """
    n = len(ts)
    rolling = static_index is None
    if rolling and indices is None:
        indices = np.arange(0,n)
    if not rolling and indices is None:
        raise ValueError("If making static predictions, indices must be "
                         "supplied.")
    N = len(indices)
    indices = np.sort(indices)
    max_index = indices[-1]
    theta, ose = innov_alg(vcm)
    preds = np.zeros(N); errs = np.zeros(N)
    get_osa = True
    if rolling:
        if max_index >= n+h:
            raise ValueError("The maximum index to be predicted must be less "
                             "than len(ts) + h.")
        if h==1: get_osa=False
        # why is there -h below?
        osa_end = max(max_index+1-h, 0)
    else:
        osa_end = static_index+1
    if get_osa:
        tmp = (innov_alg_preds(ts, vcm, 
                               indices=np.arange(0, osa_end))["preds"])
    else:
        #tmp = preds
        # think below is right
        tmp = np.zeros(max_index+1)
    for i, q in enumerate(indices):
        do_not_predict = False
        if not rolling: 
            h = q - static_index
            if h <= 0:
                preds[i] = ts[q]
                errs[i] = np.nan
                do_not_predict = True
        if rolling and q < h: 
            # not sure whether below is correct?
            preds[i] = 0
            errs[i] = vcm[i,i]
            do_not_predict = True
        if do_not_predict is False:
            preds[i] = np.dot(theta[q-1, h-1:q][::-1], (ts[0:q-h+1]-
                 tmp[0:q-h+1]))
            errs[i] = (vcm[q,q] - np.dot((theta[q-1, h-1:q]**2)[::-1], 
                ose[0:q-h+1]))
    return {"preds":preds, "sigma2":errs}