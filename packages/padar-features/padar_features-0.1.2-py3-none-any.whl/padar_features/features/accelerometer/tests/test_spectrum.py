import numpy as np
from ....libs.signal_generator import SignalGenerator
from ..spectrum import FrequencyFeature


def test_constant():
    """
    Dominant frequency and power should be very close to zero when input is
     constant signal
    """
    generator = SignalGenerator()
    data = generator.constant()
    freq_features = FrequencyFeature(data, sr=50)
    freq_features.fft().peaks()
    assert np.allclose(freq_features.dominant_frequency(n=1), np.zeros((1, 3)))
    assert np.allclose(
        freq_features.dominant_frequency_power(n=1), np.zeros((1, 3)))


def test_gaussian():
    """
    Top 10 dominant frequency power should be very close to each other (small
     standard deviation) when input is
     a random Gaussian signal
    """
    generator = SignalGenerator()
    data = generator.random_gaussian(means=[1, 0, -1], stds=[0.1, 0.1, 0.1])
    freq_features = FrequencyFeature(data, sr=50)
    freq_features.fft().peaks()
    top_n = range(1, 11)
    top_n_dominant_frequencies = np.concatenate(
        list(map(freq_features.dominant_frequency_power, top_n)), axis=0)
    std_top_n_dfs = np.std(top_n_dominant_frequencies, axis=0)
    assert np.all(std_top_n_dfs < 0.001)


def test_sinusoid():
    """
    Dominant frequency should be the 3Hz for a 3Hz sinusoidal signal. Only
     first dominant frequency exists.
    """
    generator = SignalGenerator(sr=100)
    data = generator.sinusoid(noise_stds=[0, 0, 0])
    freq_features = FrequencyFeature(data, sr=100)
    freq_features.fft().peaks()
    dom_freqs = freq_features.dominant_frequency(n=1)
    dom_freqs_second = freq_features.dominant_frequency(n=2)
    assert np.allclose(dom_freqs, np.array([1, 2, 3]))
    assert np.allclose(dom_freqs_second, np.array([-1, -1, -1]))


def test_double_sinusoid():
    """
    For a double sinusoidal signal, the first and second dominant frequencies
     3Hz (amplitude 3) and 0.3Hz (amplitude 0.3), and the third dominant
     frequency should not exist.
    """
    generator = SignalGenerator(sr=100)
    data1 = generator.sinusoid(noise_stds=[0.1, 0.1, 0.1])
    data2 = generator.sinusoid(dom_freqs=[0.1, 0.2, 0.3], amps=[0.1, 0.2, 0.3])
    data = data1 + data2
    freq_features = FrequencyFeature(data, sr=100)
    freq_features.fft().peaks()
    dom_freqs = freq_features.dominant_frequency(n=1)
    dom_freqs_second = freq_features.dominant_frequency(n=2)
    dom_freqs_third = freq_features.dominant_frequency(n=3)
    assert np.allclose(dom_freqs, np.array([1, 2, 3]))
    assert np.allclose(dom_freqs_second, np.array([0.1, 0.2, 0.3]))
    assert np.allclose(dom_freqs_third, np.array([-1, -1, -1]))
