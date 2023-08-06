
from datetime import datetime
import pandas as pd
import os
# surely there is a cleaner way!?
import tsmodels as ts

direct = os.path.split(ts.__file__)

def get_facebook_returns():
    """
    Returns a pandas series containing the natural logarithm of 
    facebook's returns.
    """
    date_parser = lambda x : datetime.strptime(x, "%d/%m/%Y")
    return pd.read_csv(direct + "/data/facebook_returns.csv", index_col=0, 
                       parse_dates=True, squeeze=True, date_parser=date_parser)
    
def get_apple_returns():
    """
    Returns a pandas series containing the natural logarithm of 
    apple's returns.
    """
    date_parser = lambda x : datetime.strptime(x, "%d/%m/%Y")
    return pd.read_csv(direct + "/data/apple_returns.csv", index_col=0, 
                       parse_dates=True, squeeze=True, date_parser=date_parser)
    
    