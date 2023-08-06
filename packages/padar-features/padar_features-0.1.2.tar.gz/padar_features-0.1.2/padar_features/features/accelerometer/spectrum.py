"""
=======================================================================
Frequency features
=======================================================================
'''Frequency domain features for numerical time series data'''
"""
from scipy import signal, interpolate
import numpy as np
from ...libs.signal_processing.detect_peaks import detect_peaks
from .. import validator
from .. import formatter
import logging

logger = logging.getLogger()


class FrequencyFeature:
    def __init__(self, X, sr, freq_range=None):
        self._check_input(X)
        self._X = X
        self._sr = sr
        self._freq_range = freq_range
        logger.info('SR=' + str(sr))

    def _check_input(self, X):
        if not validator.is_xyz_inertial(X) and not validator.is_vm_inertial(X):
            raise ValueError(
                '''Input numpy array must be a 3 axis sensor or in vector
                 magnitude''')

    def fft(self):
        freq, time, Sxx = signal.spectrogram(
            self._X,
            fs=self._sr,
            window='hamming',
            nperseg=self._X.shape[0],
            noverlap=0,
            detrend='constant',
            return_onesided=True,
            scaling='density',
            axis=0,
            mode='psd')
        # interpolate to get values in the freq_range
        if self._freq_range is not None:
            self._freq = interpolate(freq, Sxx)
            Sxx_interpolated = interpolate_f(freq_range)
        else:
            self._freq = freq
            Sxx_interpolated = Sxx
        Sxx_interpolated = np.squeeze(Sxx_interpolated)
        self._Sxx = formatter.vec2colarr(Sxx_interpolated)
        return self

    def dominant_frequency(self, n=1):
        if hasattr(self, '_freq_peaks'):
            result = list(
                map(
                    lambda i: self._freq_peaks[i][n -
                                                  1] if
                    len(self._freq_peaks[i]) >= n else -1,
                    range(0, self._Sxx.shape[1])))
            result = formatter.vec2rowarr(np.array(result))
            result = formatter.add_name(
                result, self.dominant_frequency.__name__)
            return result
        else:
            raise ValueError('Please run spectrogram and peaks methods first')

    def dominant_frequency_power(self, n=1):
        if hasattr(self, '_Sxx_peaks'):
            result = list(
                map(
                    lambda i: self._Sxx_peaks[i][n -
                                                 1] if
                    len(self._Sxx_peaks[i]) >= n else -1,
                    range(0, self._Sxx.shape[1])))
            result = formatter.vec2rowarr(np.array(result))
            result = formatter.add_name(
                result, self.dominant_frequency_power.__name__)
            return result
        else:
            raise ValueError('Please run spectrogram and peaks methods first')

    def total_power(self):
        if hasattr(self, '_Sxx'):
            result = formatter.vec2rowarr(np.sum(self._Sxx, axis=0))
            result = formatter.add_name(result, self.total_power.__name__)
            return result
        else:
            raise ValueError('Please run spectrogram first')

    def limited_band_dominant_frequency(self, low=0, high=np.inf, n=1):
        def _limited_band_df(i):
            freq = self._freq_peaks[i]
            indices = (freq >= low) & (freq <= high)
            limited_freq = freq[indices]
            return limited_freq[n-1]
        if not hasattr(self, '_freq_peaks'):
            raise ValueError('Please run spectrogram and peaks methods first')

        result = list(
            map(_limited_band_df,
                range(0, self._Sxx.shape[1])))

        result = formatter.vec2rowarr(np.array(result))
        result = formatter.add_name(
            result, self.limited_band_dominant_frequency.__name__)
        return result

    def limited_band_dominant_frequency_power(self, low=0, high=np.inf, n=1):
        def _limited_band_df_power(i):
            freq = self._freq_peaks[i]
            Sxx = self._Sxx_peaks[i]
            indices = (freq >= low) & (freq <= high)
            limited_Sxx = Sxx[indices]
            return limited_Sxx[n-1]
        if not hasattr(self, '_freq_peaks'):
            raise ValueError('Please run spectrogram and peaks methods first')

        result = list(
            map(_limited_band_df_power,
                range(0, self._Sxx.shape[1])))

        result = formatter.vec2rowarr(np.array(result))
        result = formatter.add_name(
            result, self.limited_band_dominant_frequency_power.__name__)
        return result

    def limited_band_total_power(self, low=0, high=np.inf):
        if not hasattr(self, '_freq'):
            raise ValueError('Please run spectrogram first')
        indices = (self._freq >= low) & (self._freq <= high)
        limited_Sxx = self._Sxx[indices, :]
        limited_total_power = formatter.vec2rowarr(np.sum(limited_Sxx, axis=0))
        limited_total_power = formatter.add_name(
            limited_total_power, self.limited_band_total_power.__name__)
        return limited_total_power

    def highend_power(self):
        if hasattr(self, '_Sxx'):
            result = self.limited_band_total_power(low=3.5)
            result = formatter.add_name(
                result.values, self.highend_power.__name__)
            return result
        else:
            raise ValueError('Please run spectrogram first')

    def dominant_frequency_power_ratio(self, n=1):
        result = np.divide(self.dominant_frequency_power(n=n).values,
                           self.total_power().values)
        result = formatter.add_name(
            result, self.dominant_frequency_power_ratio.__name__)
        return result

    def middlerange_dominant_frequency(self):
        result = self.limited_band_dominant_frequency(low=0.6, high=2.6, n=1)
        result = formatter.add_name(
            result.values, self.middlerange_dominant_frequency.__name__)
        return result

    def middlerange_dominant_frequency_power(self):
        result = self.limited_band_dominant_frequency_power(low=0.6, high=2.6,
                                                            n=1)
        result = formatter.add_name(
            result.values, self.middlerange_dominant_frequency_power.__name__)
        return result

    def peaks(self):
        def _sort_peaks(i, j):
            if len(i) == 0:
                sorted_freq_peaks = np.array([0])
                sorted_Sxx_peaks = np.array([np.nanmean(self._Sxx, axis=0)[j]])
            else:
                freq_peaks = self._freq[i]
                Sxx_peaks = self._Sxx[i, j]
                sorted_i = np.argsort(Sxx_peaks)
                sorted_i = sorted_i[::-1]
                sorted_freq_peaks = freq_peaks[sorted_i]
                sorted_Sxx_peaks = Sxx_peaks[sorted_i]
            logger.debug('sxx:' + str(j) + ":" + str(sorted_Sxx_peaks.shape))
            logger.debug('freq:' + str(j) + ":" + str(sorted_freq_peaks.shape))
            return (sorted_freq_peaks, sorted_Sxx_peaks)

        n_axis = self._Sxx.shape[1]
        m_freq = self._Sxx.shape[0]
        # at least 0.1 Hz different when looking for peak
        mpd = int(np.ceil(1.0 / (self._freq[1] - self._freq[0]) * 0.1))
        # print(self._Sxx.shape)
        i = list(map(lambda x: detect_peaks(
            x, mph=1e-5, mpd=mpd), list(self._Sxx.T)))
        j = range(0, n_axis)
        result = list(map(_sort_peaks, i, j))
        self._freq_peaks = list(map(lambda x: x[0], result))
        self._Sxx_peaks = list(map(lambda x: x[1], result))
        return self
