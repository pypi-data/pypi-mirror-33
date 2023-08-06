
from datetime import datetime
import pandas as pd

def get_facebook_returns():
    """
    Returns a pandas series containing the natural logarithm of 
    facebook's returns.
    """
    date_parser = lambda x : datetime.strptime(x, "%d/%m/%Y")
    return pd.read_csv("tsmodels/data/facebook_returns.csv", index_col=0, 
                       parse_dates=True, squeeze=True, date_parser=date_parser)
    
def get_apple_returns():
    """
    Returns a pandas series containing the natural logarithm of 
    apple's returns.
    """
    date_parser = lambda x : datetime.strptime(x, "%d/%m/%Y")
    return pd.read_csv("tsmodels/data/apple_returns.csv", index_col=0, 
                       parse_dates=True, squeeze=True, date_parser=date_parser)
    
    