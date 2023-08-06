import numpy as np
import pandas as pd
from datetime import datetime


class SignalGenerator:
    def __init__(self, sr=50, grange=6, duration=60):
        self._sr = sr
        self._grange = grange
        self._duration = duration

    def set_sr(self, sr):
        self._sr = sr
        return self

    def set_grange(self, grange):
        self._grange = grange
        return self

    def set_duration(self, duration):
        self._duration = duration
        return self

    def get_timestamps(self):
        st = datetime.now()
        periods = int(np.ceil(self._duration * self._sr))
        timestamps = pd.date_range(
            start=st, end=st + pd.Timedelta(self._duration, unit='s'),
            periods=periods)
        return timestamps

    def constant(self, n_axis=3, return_type='array'):
        ts = self.get_timestamps()

        data = np.concatenate(
            list(map(
                lambda i: np.reshape(
                    np.repeat(
                        np.random.rand(1), len(ts), axis=0), (len(ts), 1)),
                range(0, n_axis))),
            axis=1)
        if return_type == 'array':
            return data
        elif return_type == 'dataframe':
            return pd.DataFrame(data=data, index=ts)

    def random_gaussian(self, means=[0, 0, 0], stds=[1, 1, 1],
                        return_type='array'):
        ts = self.get_timestamps()

        data = np.concatenate(
            list(
                map(
                    lambda i: np.random.normal(
                        means[i], stds[i], (len(ts), 1)), range(0, len(means)))
            ),
            axis=1)
        if return_type == 'array':
            return data
        elif return_type == 'dataframe':
            return pd.DataFrame(data=data, index=ts)

    def sinusoid(self, dom_freqs=[1, 2, 3], init_phases=[0, 0, 0],
                 amps=[1, 2, 3],
                 noise_stds=[0.1, 0.1, 0.1], return_type='array'):
        ts = self.get_timestamps()
        ts_num = np.array(list(map(lambda x: x.timestamp(), ts.tolist())))
        data = np.concatenate(
            list(
                map(
                    lambda i:
                    np.reshape(
                        np.sin(2*np.pi*dom_freqs[i]*ts_num +
                               init_phases[i])*amps[i] +
                        np.random.normal(0, noise_stds[i]),
                        (len(ts), 1)
                    ),
                    range(0, len(dom_freqs)),
                )
            ),
            axis=1
        )
        if return_type == 'array':
            return data
        elif return_type == 'dataframe':
            return pd.DataFrame(data=data, index=ts)


if __name__ == '__main__':
    print(SignalGenerator().constant(return_type='dataframe'))
    print(SignalGenerator().random_gaussian(
        means=[0, 1, -1], stds=[0.1, 0.5, 0.1], return_type='dataframe')
        .mean(axis=0))
    print(SignalGenerator().sinusoid(return_type='dataframe').head())
