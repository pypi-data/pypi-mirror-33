
import numpy as np

class LinearModel:
    """
    Fits a linear model to data.
    
    Notes
    -----
    Currently just computes the parameters.
    """
    def __init__(self, x, y):
        """
        Parameters
        ----------
        x : np.matrix
            Contains the explanatory variables.
        y : np.matrix
            Contains the response variables.
        """
        self.x = x; self.y = y
        self.pars = (np.array(np.linalg.inv(x.transpose()*x)*
                              x.transpose()*y).flatten())