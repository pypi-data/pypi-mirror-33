
from scipy.optimize import minimize
import pandas as pd
import numpy as np
from tsmodels.classes.tsm_ARMA import ARMA 
from tsmodels.classes.tsm_Prediction import Prediction 
from tsmodels.classes.tsm_TSModel import TSModel
from tsmodels.functions.tsm_arma_garch_obj_funs import arma_garch_llh
from tsmodels.functions.tsm_arma_garch_forecast import arma_garch_forecast
#from tsmodels.settings.tsm_settings import it
from datetime import datetime

class ARMA_GARCH(TSModel):
    """
    Fits an ARMA-GARCH model to data.
    
    Parameters
    ----------
    data : pd.Series
        Must have datetime index.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
    variance_model : dict
        A dictionary of the form {'garch' : garch_type, 'order' : [m, s],
        'innov_dist' : innov_dist} where innov_dist is "norm", "ged" or "t".
    trace : dict
        Should have a "silent" key with a boolean value indicating whether to 
        print the optimiser's progress. May also have a "gap" key with an
        integer value defining the gap between printed iterations. E.g., 
        {"silent":True, "gap":5}. If "gap" key is not supplied, the gap 
        defaults to 10.
    name : str
        The name of the time series.
    """
    def __init__(self, data, mean_model = {"order":[1,1]}, variance_model = 
                                           {"order":[1,1], "innov_dist":"norm"}, 
                                           trace={"silent":True, "gap":None}, 
                                           name="Time Series"):
        super().__init__(data, name)
        vals = data.values
        TINY = 1.0e-16
        silent = trace["silent"]
        self.n = len(vals)
        self.variance_model = variance_model
        self.mean_model = mean_model
        p, q = mean_model["order"]; m, s = variance_model["order"]
        innov_dist = variance_model["innov_dist"]
        # initialise arma parameters with ARMA; method="mle-css" is too slow to 
        # use, but would be better to use in future
        arma_pars = ARMA(data, mean_model, method="css").pars[:-1]
        # initialise alpha and beta similarly to fGarch
        if m!=0: alpha_start=0.05
        else: alpha_start=0
        if s!=0: beta_start=0.9
        else: beta_start=0     
        omega_par = np.array([np.var(vals, ddof=1)*(1 - alpha_start - 
                              beta_start)])
        alpha_pars = np.repeat(alpha_start/(m + TINY), m)
        beta_pars = np.repeat(beta_start/(s + TINY), s)
        x0 = np.concatenate([arma_pars, omega_par, alpha_pars, beta_pars])
        # next set param limits
        #bounds = ([(-10*abs(np.mean(vals)), 10*abs(np.mean(vals)))] + 
        bounds = ([(None, None)] + 
                   [(None, None)]*(p+q) + 
                   [(0, None)] +
                   [(0, None)]*(m+s))
        # add shape parameter if innov_dist in ["ged", "t"]
        if innov_dist in ["ged", "t"]:
            if innov_dist == "ged":
                shape_par = 2.0
                bounds += [(0, None)]
            else:
                shape_par = 4.0
                bounds += [(2.0, None)]
            x0 = np.concatenate([x0, [shape_par]])
        nloglik = (lambda pars : arma_garch_llh(pars, vals, mean_model, 
                                                variance_model))
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
        opt = minimize(nloglik, x0, method="L-BFGS-B", jac=False, 
                       bounds=bounds, callback=callback, 
                       options={"maxiter": 50, "ftol": 1e-10}) 
        self.pars = opt.x
        self.llh = -opt.fun
        # we include attributes below for convenience
        self.mu = self.pars[0]
        self.phi = self.pars[1:p+1]
        self.theta = self.pars[p+1:p+q+1]
        self.omega = self.pars[p+q+1]
        self.alpha = self.pars[p+q+2:p+q+m+2]
        self.beta = self.pars[p+q+m+2:p+q+m+s+2]
        # self.mean is is the unconditional, constant, mean 
        # of the series
        self.mean = self.mu/(1.0 - np.sum(self.phi))
        if innov_dist in ["ged", "t"]:
            self.shape = self.pars[p+q+m+s+2]
        else:
            self.shape = None
    def predict(self, start_date=None, end_date=None, h=1, static_date=None, 
                conf_level=0.95):
        """
        Forecasts time series values. If static_index is None, h step ahead 
        predictions are made for each index using all available information 
        prior to that index. Otherwise static predictions are made using all 
        information up to and including the static_index.
        
        Parameters
        ----------
        start_date : str or None
            The start date for predictions. Must have format "%d/%m/%Y". 
            Defaults to first date in data.
        end_date : str or None
            The end date for predictions. Must have format "%d/%m/%Y". 
            Defaults to last date in data.
        h : int
            If static_date is None, h-step ahead rolling predictions will be 
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
            str_static_date = static_date
            static_date = datetime.strptime(static_date, "%d/%m/%Y")
            # must check that static_date is in the index
            static_index = self.data.index.get_loc(static_date)
        else:
            str_static_date = None
            static_index=None
        range_1 = pd.date_range(data_start_date, start_date, 
                                    freq=self.freq)
        end_1 = range_1[-1].to_pydatetime()
        range_2 = pd.date_range(data_start_date, end_date, 
                                    freq=self.freq)
        start_index=len(range_1)-1; end_index=len(range_2)-1
        # code below is needed to ensure that predictions are made for
        # all times between start_date and end_date
        if end_1 < start_date:
            start_index += 1
        date_range = pd.date_range(start_date, end_date, freq=self.freq)
        indices = np.arange(start_index, end_index+1)
        pars = {"mu":self.mu, "phi":self.phi, "theta":self.theta, "omega":
            self.omega, "alpha":self.alpha, "beta":self.beta, 
            "shape":self.shape}
        res = arma_garch_forecast(self.data.values, pars, 
                                   self.variance_model["innov_dist"], h, 
                                   static_index, indices, conf_level)
        return Prediction(self.data, date_range, res["preds"], 
                           res["upper_bounds"], res["lower_bounds"], 
                           conf_level, self.name, str_static_date, h)

class ARMA_GARCH1(TSModel):
    """
    Fits an ARMA-GARCH model to data.
    
    Parameters
    ----------
    data : pd.Series
        Must have datetime index.
    mean_model : dict
        A dictionary of the form {'order' : [p, q]}.
    variance_model : dict
        A dictionary of the form {'garch' : garch_type, 'order' : [m, s],
        'innov_dist' : innov_dist} where innov_dist is "norm", "ged" or "t".
    trace : dict
        Should have a "silent" key with a boolean value indicating whether to 
        print the optimiser's progress. May also have a "gap" key with an
        integer value defining the gap between printed iterations. E.g., 
        {"silent":True, "gap":5}. If "gap" key is not supplied, the gap 
        defaults to 10.
    name : str
        The name of the time series.
    """
    def __init__(self, data, mean_model = {"order":[1,1]}, variance_model = 
                                           {"order":[1,1], "innov_dist":"norm"}, 
                                           trace={"silent":True, "gap":None}, 
                                           name="Time Series"):
        super().__init__(data, name)
        vals = data.values
        TINY = 1.0e-16
        silent = trace["silent"]
        self.n = len(vals)
        self.variance_model = variance_model
        self.mean_model = mean_model
        p, q = mean_model["order"]; m, s = variance_model["order"]
        innov_dist = variance_model["innov_dist"]
        # initialise arma parameters with ARMA; method="mle-css" is too slow to 
        # use, but would be better to use in future
        arma_pars = ARMA(data, mean_model, method="css").pars[:-1]
        # initialise alpha and beta as done in fGarch R package; cannot simply 
        # set alpha_start=0.1 and beta_start=0.8 otherwise problems arise when 
        # m=0 and/or s=0
        if m!=0: alpha_start=0.1
        else: alpha_start=0
        if s!=0: beta_start=0.8
        else: beta_start=0     
        omega_par = np.array([np.var(vals, ddof=1)*(1 - alpha_start - 
                              beta_start)])
        alpha_pars = np.repeat(alpha_start/(m + TINY), m)
        beta_pars = np.repeat(beta_start/(s + TINY), s)
        x0 = np.concatenate([arma_pars, omega_par, alpha_pars, beta_pars])
        # next set param limits
        bounds = ([(-10*abs(np.mean(vals)), 10*abs(np.mean(vals)))] + 
                   [(-1 + TINY, 1 - TINY)]*(p+q) + 
                   [(TINY*np.var(vals, ddof=1), 100*np.var(vals, ddof=1))] + 
                   [(TINY, 1 - TINY)]*(m+s))
        # add shape parameter if innov_dist in ["ged", "t"]
        if innov_dist in ["ged", "t"]:
            # initialise shape_par as 4
            shape_par = 4.0
            x0 = np.concatenate([x0, [shape_par]])
            if innov_dist == "ged":
                # shape_par must be between 0 and inf
                bounds += [(TINY, None)]
            if innov_dist == "t":
                # shape_par must be between 2 and inf
                bounds += [(2.0+TINY, None)]
        nloglik = (lambda pars : arma_garch_llh(pars, vals, mean_model, 
                                                variance_model))
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
        opt = minimize(nloglik, x0, method="SLSQP", jac=False, 
                       bounds=bounds, callback=callback, 
                       options={"maxiter": 100, "ftol": 1e-14}) 
        self.pars = opt.x
        self.llh = -opt.fun
        # we include attributes below for convenience
        self.mu = self.pars[0]
        self.phi = self.pars[1:p+1]
        self.theta = self.pars[p+1:p+q+1]
        self.omega = self.pars[p+q+1]
        self.alpha = self.pars[p+q+2:p+q+m+2]
        self.beta = self.pars[p+q+m+2:p+q+m+s+2]
        # self.mean is is the unconditional, constant, mean 
        # of the series
        self.mean = self.mu/(1.0 - np.sum(self.phi))
        if innov_dist in ["ged", "t"]:
            self.shape = self.pars[p+q+m+s+2]
    def predict(self, h=1, static_index=None, indices=None):
        """
        Forecasts time series values. If static_index is None, h step ahead 
        predictions are made for each index using all available information 
        prior to that index. Otherwise static predictions are made using all 
        information up to and including the static_index.
        
        Parameters
        ----------
        indices : list or range
            The indices of the time series to predict; 0 is the index of the 
            first time series point, 1 is the index of the second, etc. If is 
            None, defaults to all of the indices in the time series.
        h : int
            If static_index is None, h step ahead predictions are made for 
            each index in indices.
        static_index : int or None
            If an index is given, all information up to and including this index 
            will be used to make the predictions.
            
        Returns
        -------
        pred : datamodels.ts.classes.Prediction
            A Prediction object.
            
        Notes
        -----
        Currently static predictions cannot be made and h must be 1.
        """
        if indices is None:
            indices = np.arange(0,self.n)
        indices = np.array(indices)
        pars = {"mu":self.mu, "phi":self.phi, "theta":self.theta, "omega":
            self.omega, "alpha":self.alpha, "beta":self.beta}
        res = arma_garch_forecast(self.data.values, pars, h, static_index, 
                                  indices)
        return Prediction(self.data, res["preds"], res["sigma2"], indices, 
                          self.name, static_index, h)