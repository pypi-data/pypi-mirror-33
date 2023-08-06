"""

Validate the input data is proper for feature computation

Author: Qu Tang

Date: Jul 10, 2018

"""
import numpy as np
import pandas as pd
from . import formatter
from datetime import datetime


def has_timestamp(X):
    return isinstance(X[0, 0], (datetime, np.datetime64, pd.Timestamp, str))


def is_xyz(X):
    return X.shape[1] == 3


def is_vm(X):
    return X.shape[1] == 1


def is_xyz_inertial(X):
    return not has_timestamp(X) and is_xyz(X)


def is_vm_inertial(X):
    return not has_timestamp(X) and is_vm(X)


def is_vector(X):
    return len(X.shape) == 1


def is_arr(X):
    return len(X.shape) == 2


def is_row_arr(X):
    return is_arr(X) and X.shape[0] == 1 and X.shape[1] >= 1


def is_col_arr(X):
    return is_arr(X) and X.shape[0] >= 1 and X.shape[1] == 1


def has_enough_samples(X, threshold=1):
    if is_vector(X):
        X = formatter.vec2colarr(X)
    return X.shape[0] >= threshold
