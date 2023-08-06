
from scipy.optimize import minimize
import pandas as pd
import numpy as np
from datetime import datetime
from tsmodels.functions.tsm_arma_acvf import arma_vcm
from tsmodels.functions.tsm_arma_obj_funs import (arma_mle_a, arma_mle_b, 
                                                  arma_css)
from tsmodels.functions.tsm_hannan_rissanen import hannan_rissanen
from tsmodels.functions.tsm_innov_alg import innov_alg_preds
from tsmodels.classes.tsm_TSModel import TSModel
from tsmodels.classes.tsm_Prediction import Prediction
from tsmodels.functions.tsm_densities import q_std_norm

class ARMA(TSModel):
    """
    Fits an ARMA model to data using maximum likelihood estimation or 
    conditional sum of squares.
    
    Parameters
    ----------
    data : pd.Series
        Must have datetime index.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
    method : str
        The method used to fit the model. Can be "mle-css" or "css".
    trace : dict
        Should have a "silent" key with a boolean value indicating whether to 
        print the optimiser's progress. May also have a "gap" key with an
        integer value defining the gap between printed iterations. E.g., 
        {"silent":True, "gap":5}. If "gap" key is not supplied, the gap 
        defaults to 10.
    name : str
        The name of the time series.
        
    Notes
    -----
    We currently assume that the errors are homoscedastic and normally 
    distributed. If method="mle-css", the starting values are found by 
    minimising conditional sum of squares. If method="css", the starting
    values are found using the Hannan-Rissanen algorithm.
    """
    def __init__(self, data, mean_model={"order":[1,1]}, method="mle-css", 
                                         trace={"silent":True, "gap":None}, 
                                         name=""):
        super().__init__(data, name)
        vals = data.values
        self.n = len(vals)
        self.mean_model = mean_model
        p, q = mean_model["order"]
        silent = trace["silent"]
        bounds = ([(None, None)] + 
                   [(None, None)]*(p+q))
        if method == "mle-css":
            # use method="css" to obtain starting values
            x0 = ARMA(data, mean_model, method="css").pars
            bounds += [(0, None)]
            # arma_mle_a is faster than arma_mle_b
            fun = (lambda pars : arma_mle_a(pars, vals, mean_model))
        elif method == "css":
            hr = hannan_rissanen(vals, p, q)
            x0 = hr[0:p+q+1]
            fun = (lambda pars : arma_css(pars, vals, mean_model))
        if silent==False:
            if "gap" in trace:
                gap = trace["gap"]
            else:
                # gap defaults to 10
                gap = 10
            global it
            it = 0
            def callback(xk):
                global it
                if it%gap == 0:
                    print("Iteration: ", it)
                    print("Parameters: ", xk)
                it += 1
        else:
            callback = None
        opt = minimize(fun, x0, method="L-BFGS-B", jac=False, bounds=bounds, 
                       callback=callback, options={"maxiter": 1000, 
                                                   "ftol": 1e-10})
        self.pars = opt.x
        if method == "mle-css":
            self.llh = -opt.fun
        if method == "css":
            # add hannan-rissanen estimate of sigma
            self.pars = np.concatenate([self.pars, [hr[p+q+1]]])
        # we include attributes below for convenience
        self.mu = self.pars[0]
        self.phi = self.pars[1:p+1]
        self.theta = self.pars[p+1:p+q+1]
        self.sigma = self.pars[p+1+q]
        # self.mean is is the unconditional, constant, mean of the series
        self.mean = self.mu/(1.0 - np.sum(self.phi))
    def predict(self, start_date=None, end_date=None, h=1, static_date=None, 
                conf_level=0.95):
        """
        Forecasts time series values. If static_date is None, h step ahead 
        predictions are made for each index using all available information 
        prior to that index. Otherwise static predictions are made using all 
        information up to and including the static_date.
        
        Parameters
        ----------
        start_date : str or None
            The start date for predictions. Must have format "%d/%m/%Y". 
            Defaults to first date in data.
        end_date : str or None
            The end date for predictions. Must have format "%d/%m/%Y". 
            Defaults to last date in data.
        h : int
            If static_index is None, h-step ahead rolling predictions will be 
            made.
        static_date : str or None
            If a date is given, all information up to and including this 
            date will be used to make static predictions.
        conf_level : float
            The computed prediction intervals will contain the true values
            will probability equal to conf_level.
            
        Returns
        -------
        pred : tsmodels.classes.Prediction
            A Prediction object.
        """
        data_start_date = self.data.index[0].to_pydatetime()
        data_end_date = self.data.index[-1].to_pydatetime()
        if start_date is None:
            start_date = datetime.strftime(data_start_date, "%d/%m/%Y")
        if end_date is None:
            end_date = datetime.strftime(data_end_date, "%d/%m/%Y")
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        if start_date < data_start_date:
            raise ValueError("start_date cannot be earlier than the start "
                             "date in data.")
        if static_date is not None:
            static_date = datetime.strptime(static_date, "%d/%m/%Y")
            # must check that static_date is in the index
            static_index = self.data.index.get_loc(static_date)
        else:
            static_index=None
        start_index = len(pd.date_range(data_start_date, start_date, 
                                        freq=self.freq))-1
        end_index = len(pd.date_range(data_start_date, end_date, 
                                        freq=self.freq))-1
        date_range = pd.date_range(start_date, end_date, freq=self.freq)
        # use arma_vcm below instead                                   
        vcm = arma_vcm(self.phi, self.theta, end_index+1, self.sigma)
        indices = np.arange(start_index, end_index+1)
        res = innov_alg_preds(self.data.values, vcm, h, static_index, indices)
        # reference where it said to add mean to the predictions of the de-
        # meaned series
        res["preds"] += self.mean
        # currently we only allow for normal errors
        lp = (1.0-conf_level)/2.0; up = 1.0 - lp
        upper_bounds = res["preds"] + q_std_norm(up)*np.sqrt(res["sigma2"])
        lower_bounds = res["preds"] + q_std_norm(lp)*np.sqrt(res["sigma2"])
        return Prediction(self.data, date_range, res["preds"], upper_bounds, 
                          lower_bounds, conf_level, self.name, static_index, h)