"""

Formatting data structure (numpy array or pandas dataframe) to desired
 structure

Author: Qu Tang

Date: Jul 10, 2018

"""
from . import validator
import numpy as np
import pandas as pd


def vec2rowarr(X):
    if len(X.shape) == 1:
        return np.reshape(X, (1, X.shape[0]))
    elif len(X.shape) == 2:
        return X
    elif len(X.shape) > 2:
        raise NotImplementedError('''vec2rowarr only accepts 1D or 2D numpy
         array''')
    else:
        return np.nan


def vec2colarr(X):
    if len(X.shape) == 1:
        return np.reshape(X, (X.shape[0], 1))
    elif len(X.shape) == 2:
        return X
    elif len(X.shape) > 2:
        raise NotImplementedError('''vec2colarr only accepts 1D or 2D numpy
         array''')


def vec2arr(X, data_type='raw'):
    if validator.is_vector(X):
        if data_type == 'raw':
            return vec2colarr(X)
        elif data_type == 'feature':
            return vec2rowarr(X)
    else:
        return X


def want_axis(X, want='xyz'):
    if want == 'xyz':
        return X
    elif want == 'x':
        return X[:, 0]
    elif want == 'y':
        return X[:, 1]
    elif want == 'z':
        return X[:, 2]


def as_float64(X):
    return X.astype(np.float64)


def rowarr2df(X, st, et):
    df = pd.DataFrame(index=[0], data=X, columns=range(0, X.shape[1]))
    df.insert(0, 'START_TIME', st)
    df.insert(1, 'STOP_TIME', et)
    df = df.set_index(['START_TIME', 'STOP_TIME'])
    return df


def add_name(X, name):
    n_dim = X.shape[1]
    names = [name.upper() + '_' + str(n) for n in range(0, n_dim)]
    result = pd.DataFrame(data=X, columns=names)
    return result