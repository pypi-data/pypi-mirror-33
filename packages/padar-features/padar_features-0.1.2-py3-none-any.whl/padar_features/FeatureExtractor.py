"""

Feature extractor top-level interface

"""
import pandas as pd
from clize import run
import numpy as np
from glob import glob
from dask import delayed
from .features import parser
import logging
import functools
from dask.diagnostics import ResourceProfiler
import time

logger = logging.getLogger()


def rowarr2df(X, st, et):
    df = pd.DataFrame(index=[0], data=X, columns=range(0, X.shape[1]))
    df.insert(0, 'START_TIME', st)
    df.insert(1, 'STOP_TIME', et)
    df = df.set_index(['START_TIME', 'STOP_TIME'])
    return df


def append_time(df, st, et):
    df.insert(0, 'START_TIME', st)
    df.insert(1, 'STOP_TIME', et)
    df = df.set_index(['START_TIME', 'STOP_TIME'])
    return df


class FeatureExtractor:
    def __init__(self, segment='sliding',
                 window_size=12.8, step_size=12.8):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self._segment = segment
        self._ws = window_size
        self._ss = step_size
        self._rprof = ResourceProfiler(dt=0.25)

    def import_data(self, file_paths, sensor_type, group_dicts=None,
                    parallel=False):
        list_of_data = []
        for file_path, group_dict in zip(file_paths, group_dicts):
            data = delayed(FeatureExtractor._import_data)(
                file_path, sensor_type)
            df_dict = {
                **group_dict,
                'DATA': data
            }
            list_of_data.append(df_dict)
        self._data = list_of_data
        return self

    @staticmethod
    def _import_data(file_path, sensor_type):
        if sensor_type == 'accelerometer':
            data = pd.read_csv(file_path, parse_dates=[0],
                               infer_datetime_format=True,
                               usecols=range(0, 4))
            data.columns = ['HEADER_TIME_STAMP', 'X', 'Y', 'Z']
        return data

    def _no_segment(self, func):
        data = delayed(pd.concat)([df_dict['DATA']
                                   for df_dict in self._data], axis=0)
        result_df = delayed(self._compute_on_chunk)(func, data)
        result_df = delayed(lambda df: df.T)(result_df)
        return result_df

    def _compute_on_chunk(self, func, data):
        data = data.set_index(data.columns[0])
        result_df = func(data.values)
        result_df = append_time(
            result_df, st=data.index.values[0], et=data.index.values[-1])
        return result_df

    def _segment_by_file(self, func):
        result_dfs = []
        for df_dict in self._data:
            data = df_dict['DATA']
            result_df = delayed(self._compute_on_chunk)(func, data)
            result_df = delayed(
                lambda df: df.assign(PATH=df_dict['PATH']))(result_df)
            result_dfs.append(result_df)
        return delayed(pd.concat)(result_dfs, axis=0)

    def _segment_by_sliding(self, func):
        data = self._data.set_index(self._data.columns[0])
        freq = str(self._ws * 1000) + 'L'
        result_df = data.groupby(pd.Grouper(level='HEADER_TIME_STAMP',
                                            freq=freq,
                                            closed='right')).apply(
            lambda rows: rowarr2df(
                func(rows.values), st=rows.index.values[0],
                et=rows.index.values[-1])
        )
        result_df.columns = [func.__name__.upper(
        ) + '_' + str(col) for col in result_df.columns]
        return result_df

    def worflow_graph(self):
        self._workflow.visualize(filename='workflow.svg')

    def workflow_profile(self):
        self._rprof.visualize()
        self._rprof.close()

    def compute(self, func, **kwargs):
        if self._segment == 'no':
            func_ = functools.partial(func, **kwargs)
            result_df = self._no_segment(func_)
        elif self._segment == 'file':
            func_ = functools.partial(func, **kwargs)
            result_df = self._segment_by_file(func_)
        elif self._segment == 'sliding':
            return self._segment_by_sliding(func)
        else:
            raise NotImplementedError("Other segment mode is not implemented")
        self._workflow = result_df
        self._rprof.register()
        computed_result_df = result_df.compute(scheduler='threads')
        self._rprof.unregister()
        return computed_result_df

    @staticmethod
    def cmd(func):
        def _extract_groups(file_paths):
            return [
                {'PID': parser.get_pid(file_path),
                 'SID': parser.get_sensor_id(file_path),
                 'PATH': file_path
                 } for file_path in file_paths
            ]

        def _extract_group_dicts(file_paths, format_type):
            if format_type == 'mhealth':
                group_dicts = _extract_groups(file_paths)
            else:
                group_dicts = [{'GROUP_ID': file_path}
                               for file_path in file_paths]
            return group_dicts

        def wrapped_func(file_path, *,
                         output='./extracted_features_' +
                         str(int(time.time() * 1000)) + '.feature.csv',
                         workflow_graph=True,
                         sensor_type='accelerometer',
                         format_type='mhealth',
                         parallel=False,
                         verbose=False,
                         segment='no',
                         window_size=12.8, step_size=12.8, sr=50):
            if verbose:
                import sys
                logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

            extractor = FeatureExtractor(
                segment=segment, window_size=window_size, step_size=step_size)

            files = glob(file_path, recursive=True)
            if len(files) == 0:
                logger.error('Please check your input file pattern')
                exit(2)
            logger.info('list of files:')
            [logger.info(file_path) for file_path in files]
            group_dicts = _extract_group_dicts(files, format_type)
            extractor.import_data(files, sensor_type,
                                  group_dicts)
            result = extractor.compute(func, sr=sr)
            if workflow_graph:
                extractor.worflow_graph()
            extractor.workflow_profile()
            result.to_csv(output, float_format='%.9f')
            return result
        return wrapped_func
