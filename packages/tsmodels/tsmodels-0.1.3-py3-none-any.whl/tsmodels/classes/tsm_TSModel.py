
import pandas as pd
from tsmodels.settings.tsm_settings import figsize
from tsmodels.functions.tsm_format_ts import format_ts_ax
from datetime import datetime
import matplotlib.pyplot as plt

class TSModel:
    """
    This class is used to build other time series classes in the module.
    """
    def __init__(self, data, name):
        self.data = data
        self.name= name
        # we store the frequency of the data as a pandas offset alias
        self.freq = pd.infer_freq(data.index)
    def plot_data(self, start_date=None, end_date=None):
        """
        Plots the time series between start_date and end_date.
        
        Parameters
        ----------
        start_date : str
            The start date of the plot. Must have format "%d/%m/%Y". Defaults 
            to first date of series.
        end_date : str
            The end date of the plot. Must have format "%d/%m/%Y". Defaults to 
            first date of series.
        """
        if start_date is None:
            start_date = self.data.index[0].strftime("%d/%m/%Y")
        if end_date is None:
            end_date = self.data.index[-1].strftime("%d/%m/%Y")
        title = "{} Plot Between {} and {}".format(self.name, start_date, 
                         end_date)
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(self.data)
        ax.set_title(title, loc="left", position=(0, 1.025))
        format_ts_ax(ax, start_date, end_date)
        return ax