"""
Computing features related to activation samples.

Author: Qu Tang

Date: Jul 10, 2018

References:

1. Mannini A, Rosenberger M, Haskell WL, Sabatini AM, Intille SS. Activity
 Recognition in Youth Using Single Accelerometer Placed at Wrist or Ankle. Med
 Sci Sports Exerc. 2017;49(4):801–12.
 https://www.ncbi.nlm.nih.gov/pubmed/27820724

"""

import numpy as np
from .. import validator
from .. import formatter


def active_perc(X, threshold=0.2):
    """
    The percentage of active samples, active samples are samples whose value is
     beyond certain threshold. Default is 0.2g.
    """
    _check_input(X)
    X = formatter.as_float64(X)
    thres_X = X >= threshold
    active_samples = np.sum(thres_X, axis=0)
    active_perc = formatter.vec2rowarr(
        active_samples / np.float(thres_X.shape[0]))
    return active_perc


def activation_count(X, threshold):
    """
    The number of times signal go across up the active threshold
    """
    _check_input(X)
    X = formatter.as_float64(X)
    thres_X = X >= threshold
    active_samples = np.sum(thres_X, axis=0)
    active_crossings_X = np.diff(
        np.insert(thres_X, 0, np.zeros([1, X.shape[1]]), axis=0),
        axis=0) > 0
    active_crossings = np.sum(active_crossings_X, axis=0)
    result = formatter.vec2rowarr(np.divide(active_crossings, active_samples))
    return result


def activation_std(X, threshold):
    """
    The standard deviation of the durations of actived durations
    """
    _check_input(X)
    X = formatter.as_float64(X)
    thres_X = X >= threshold
    cumsum_X = np.cumsum(thres_X, axis=0)
    rise_marker_X = np.diff(
        np.insert(thres_X, 0, np.zeros([1, X.shape[1]]), axis=0),
        axis=0) > 0
    active_crossings = np.sum(rise_marker_X, axis=0)
    zero_marker = active_crossings <= 2
    fall_marker_X = np.diff(
        np.append(thres_X, np.zeros([1, X.shape[1]]), axis=0), axis=0) < 0
    rise_X = np.sort(np.multiply(
        cumsum_X, rise_marker_X, dtype=np.float), axis=0)
    fall_X = np.sort(np.multiply(
        cumsum_X, fall_marker_X, dtype=np.float), axis=0)
    activation_dur_X = fall_X - rise_X + 1
    activation_dur_X[activation_dur_X == 1.] = np.nan
    activation_std = np.nanstd(activation_dur_X, axis=0)
    activation_std[zero_marker] = 0
    activation_std = formatter.vec2rowarr(activation_std / X.shape[0])
    return(activation_std)


def _check_input(X):
    if not validator.is_xyz_inertial(X) and not validator.is_vm_inertial(X):
        raise ValueError(
            'Input numpy array must be a 3 axis sensor or in vector magntiude')
