import numpy as np
from ....libs.signal_generator import SignalGenerator
from .. import stats


def test_gaussian():
    generator = SignalGenerator()
    data = generator.random_gaussian(means=[1, 0, -1], stds=[0.001, 0.001, 0.001])
    result = stats.mean(data).values
    assert np.allclose(result, [1, 0, -1], atol=0.001)
