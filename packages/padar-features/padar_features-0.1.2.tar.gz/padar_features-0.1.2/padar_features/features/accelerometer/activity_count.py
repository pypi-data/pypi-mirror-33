"""

Computing features about different versions of activity counts

Author: Qu Tang

Date: Jul 10, 2018

"""
from numpy.linalg import norm
from .. import validator
from .. import formatter


def enmo(X):
    """

    Computing ENMO value of accelerometer data

    Arguments:
        X {numpy.ndarray} -- 2D numpy array M x N, M is the number of samples
         and N is the dimension of the data

    Returns:
        [numpy.ndarray] -- 1 x 1
    """
    _check_input(X)
    X = formatter.as_float64(X)
    result = np.mean(np.clip(norm(X, ord=2, axis=0) - 1, a_min=0, a_max=None))
    return formatter.vec2rowarr(np.array([result]))


def _check_input(X):
    if not validator.is_xyz_inertial(X):
        raise ValueError('Input numpy array must has dimension: n x 3')