"""

Computing features about accelerometer orientations

Author: Qu Tang

Date: Jul 10, 2018
"""
import numpy as np
from numpy.linalg import norm
from .. import formatter
from .. import operator
from .. import validator
import logging


logger = logging.getLogger()


class OrientationFeature:
    def __init__(self, X, subwins=4):
        OrientationFeature.check_input(X)
        self._X = X
        self._subwins = subwins

    @staticmethod
    def check_input(X):
        if not validator.is_xyz_inertial(X):
            raise ValueError(
                'Input numpy array must be a 3 axis sensor')

    @staticmethod
    def orientation_xyz(X, unit='rad'):
        OrientationFeature.check_input(X)
        X = formatter.as_float64(X)
        if not validator.has_enough_samples(X):
            logger.warning(
                '''One of sub windows do not have enough samples, will ignore in
                feature computation''')
            orientation_xyz = np.array([np.nan, np.nan, np.nan])
        else:
            gravity = np.array(np.mean(X, axis=0), dtype=np.float)
            orientation_xyz = np.arccos(
                gravity / norm(gravity, ord=2, axis=0))
            if unit == 'deg':
                orientation_xyz = np.rad2deg(orientation_xyz)
        return formatter.vec2rowarr(orientation_xyz)

    def estimate_orientation(self, unit='rad'):
        result = operator.apply_over_subwins(
            self._X, OrientationFeature.orientation_xyz, subwins=self._subwins, unit=unit)
        self._orientations = np.concatenate(result, axis=0)
        logger.debug("Est.Orientation=" + str(self._orientations.shape))
        return self

    def median_angles(self):
        median_angles = np.nanmedian(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array(median_angles))
        result = formatter.add_name(result, self.median_angles.__name__)
        return result

    def median_x_angle(self):
        median_angles = np.nanmedian(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([median_angles[0]]))
        result = formatter.add_name(result, self.median_x_angle.__name__)
        return result

    def median_y_angle(self):
        median_angles = np.nanmedian(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([median_angles[1]]))
        result = formatter.add_name(result, self.median_y_angle.__name__)
        return result

    def median_z_angle(self):
        median_angles = np.nanmedian(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([median_angles[2]]))
        result = formatter.add_name(result, self.median_z_angle.__name__)
        return result

    def range_angles(self):
        range_angles = np.nanmax(
            self._orientations, axis=0) - np.nanmin(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array(range_angles))
        result = formatter.add_name(result, self.range_angles.__name__)
        return result

    def range_x_angle(self):
        range_angles = np.nanmax(
            self._orientations, axis=0) - np.nanmin(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([range_angles[0]]))
        result = formatter.add_name(result, self.range_x_angle.__name__)
        return result

    def range_y_angle(self):
        range_angles = np.nanmax(
            self._orientations, axis=0) - np.nanmin(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([range_angles[1]]))
        result = formatter.add_name(result, self.range_y_angle.__name__)
        return result

    def range_z_angle(self):
        range_angles = np.nanmax(
            self._orientations, axis=0) - np.nanmin(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([range_angles[2]]))
        result = formatter.add_name(result, self.range_z_angle.__name__)
        return result

    def std_angles(self):
        std_angles = np.nanstd(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array(std_angles))
        result = formatter.add_name(result, self.std_angles.__name__)
        return result

    def std_x_angle(self):
        std_angles = np.nanstd(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([std_angles[0]]))
        result = formatter.add_name(result, self.std_x_angle.__name__)
        return result

    def std_y_angle(self):
        std_angles = np.nanstd(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([std_angles[1]]))
        result = formatter.add_name(result, self.std_y_angle.__name__)
        return result

    def std_z_angle(self):
        std_angles = np.nanstd(self._orientations, axis=0)
        result = formatter.vec2rowarr(np.array([std_angles[2]]))
        result = formatter.add_name(result, self.std_z_angle.__name__)
        return result
