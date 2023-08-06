
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tsmodels.settings.tsm_settings import figsize
from tsmodels.functions.tsm_format_ts import format_ts_ax

class Prediction:
    """
    Stores prediction data and allows it to be conveniently plotted.
    
    Parameters
    ----------
    data : pd.Series
        Contains the actual time series.
    date_range : pd.DatetimeIndex
        Contains the dates for the predictions.
    preds : np.array
        Contains the predictions.
    upper_bounds : np.array
        Contains the upper bounds for the predictions.
    lower_bounds : np.array
        Contains the lower bounds for the predictions.
    conf_level : float
        The computed prediction intervals will contain the true values
        will probability equal to conf_level.
    name : str
        The name of the time series.
    static_date : int or None
    h : int
    """
    def __init__(self, data, date_range, preds, upper_bounds, lower_bounds, 
                 conf_level, name, static_date, h):
        self.conf_level = conf_level
        self.name = name
        self.static_date = static_date
        self.h = h
        sto = pd.DataFrame({"Prediction":preds,
                            "Upper Bound":upper_bounds,
                            "Lower Bound":lower_bounds},
                            index=date_range)
        data = pd.DataFrame(data); data.columns=["Observation"]
        sto = data.join(sto, how="outer").loc[date_range]
        self.prediction_data = sto
    def plot(self, start_date=None, end_date=None, typ="pred"):
        """
        Allows you to plot predictions.
        
        Parameters
        ----------
        start_date : str
            Must have format "%d/%m/%Y".
        end_date : str
            Must have format "%d/%m/%Y".
        typ : str
            The type of plot to produce. Either "pred", which plots point 
            estimates and prediction intervals, or "int_size", which plots the 
            size of the prediction intervals.
        
        Returns
        -------
        ax : matplotlib.axes.Axes
        """
        if start_date is None:
            start_date = self.prediction_data.index[0].strftime("%d/%m/%Y")
        if end_date is None:
            end_date = self.prediction_data.index[-1].strftime("%d/%m/%Y")
        if typ == "pred": ins = "s"
        if typ == "int_size": ins = " Interval Sizes"
        if self.static_date is None:
            title = "{} {}-Step Ahead Rolling Prediction{}"
            title = title.format(self.name, self.h, ins)
        else:
            title = "{} Prediction{} From Static Date {}"
            title = title.format(self.name, ins, self.static_date)
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        data = self.prediction_data[start_date:end_date]
        fig, ax = plt.subplots(figsize=figsize)
        if typ=="pred":
            ax.fill_between(data.index, 
                            data["Lower Bound"],
                            data["Upper Bound"],
                            color="#79C0E1", alpha=0.4)
            ax.plot(data["Prediction"], c="#79C0E1", lw=1.5)
            ax.scatter(data.index, 
                   data["Observation"], c="black", alpha=0.6, 
                   marker="x")
        elif typ=="int_size":
            int_size = (data["Upper Bound"]-
                        data["Lower Bound"])
            ax.plot(int_size, c="#6ec2b1")
        ax.set_title(title, loc="left", position=(0, 1.025))
        format_ts_ax(ax, start_date, end_date)
        return ax