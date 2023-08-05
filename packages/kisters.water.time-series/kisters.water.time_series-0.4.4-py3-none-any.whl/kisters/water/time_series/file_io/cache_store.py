from typing import Iterable, Any, Mapping
from datetime import datetime

import pandas as pd

from kisters.water.time_series.time_series_decorator import TimeSeriesDecorator
from kisters.water.time_series.time_series import TimeSeries
from kisters.water.time_series.time_series_store import TimeSeriesStore


class _CacheTimeSeries(TimeSeriesDecorator):
    def __init__(self, forward: TimeSeries):
        super().__init__(forward)
        self._data = None
        self._comments = None

    def _load_data_frame(self, start: datetime = None, end: datetime = None, params: Mapping = None) -> pd.DataFrame:
        if self._data is None:
            self._data = self._forward.read_data_frame(start, end, params=params)
            return self._data.copy()

        if start is None:
            start = self.coverage_from
        if end is None:
            end = self.coverage_until

        dates = self._data.index
        if start < dates[0]:
            df = self._forward.read_data_frame(start, dates[0], params=params)
            self._data = pd.concat([df[~df.index.isin(self._data.index)], self._data])
        if end > dates[-1]:
            df = self._forward.read_data_frame(dates[-1], end, params=params)
            self._data = pd.concat([self._data, df[~df.index.isin(self._data.index)]])

        if start is None and end is None:
            return self._data.copy()
        if start is None:
            return self._data.loc[self._data.index <= end].copy()
        elif end is None:
            return self._data.loc[self._data.index >= start].copy()
        else:
            return self._data.loc[(self._data.index >= start) & (self._data.index <= end)].copy()

    def write_data_frame(self, data_frame: pd.DataFrame):
        if self._data is None:
            self._data = data_frame
        else:
            self._data = pd.concat([self._data, data_frame[~data_frame.index.isin(self._data.index)]], sort=True)
            self._data.update(data_frame)

    def __first_comment(self) -> datetime:
        date = None
        for i, row in self._comments.iterrows():
            if date is None:
                date = row.loc['from']
            date = row.loc['from'] if row.loc['from'] < date else date
        return date

    def __last_comment(self) -> datetime:
        date = None
        for i, row in self._comments.iterrows():
            if date is None:
                date = row.loc['until']
            date = row.loc['until'] if row.loc['until'] > date else date
        return date

    def get_comments(self, start: datetime=None, end: datetime=None) -> pd.DataFrame:
        if self._comments is None:
            if hasattr(self._forward, 'get_comments'):
                self._comments = self._forward.get_comments(start, end)
            else:
                self._comments = pd.DataFrame()
            return self._comments.copy()

        first_comment = self.__first_comment()
        last_comment = self.__last_comment()
        if start is None:
            start = self.coverage_from
        if end is None:
            end = self.coverage_until

        if start < first_comment:
            if hasattr(self._forward, 'get_comments'):
                self.write_comments(self._forward.get_comments(start, first_comment))
        if end > last_comment:
            if hasattr(self._forward, 'get_comments'):
                self.write_comments(self._forward.get_comments(end, last_comment))

        comments = self._comments.copy()
        for i, row in comments.iterrows():
            if end < row.loc['from'] or row.loc['until'] < start:
                comments = comments.drop(i)
            else:
                if row.loc['from'] < start:
                    comments.loc[i, 'from'] = start
                if row.loc['until'] > end:
                    comments.loc[i, 'until'] = end
        return comments

    def write_comments(self, comments: pd.DataFrame):
        if self._comments is None:
            self._comments = comments
        else:
            for i, row in comments.iterrows():
                for i_, row_ in self._comments.iterrows():
                    if row.loc['comment'] == row_.loc['comment']:
                        if row.loc['from'] >= row_.loc['from'] and row.loc['until'] <= row_.loc['until']:
                            comments = comments.drop(i)
                        else:
                            drop = False
                            if row.loc['from'] < row_.loc['from'] <= row.loc['until']:
                                self._comments.loc[i_, 'from'] = row['from']
                                drop = True
                            if row.loc['until'] > row_.loc['until'] >= row.loc['from']:
                                self._comments.loc[i_, 'until'] = row['until']
                                drop = True
                            if drop:
                                comments = comments.drop(i)
            self._comments = pd.concat([self._comments, comments], ignore_index=True)

    def update_qualities(self, qualities: pd.DataFrame):
        if self._data is not None:
            q_col = list(qualities.columns)[0]
            column_list = list(self._data.columns)
            if q_col not in column_list:
                q_col_name = 'quality'
                for col in column_list:
                    if 'qualit' in col:
                        q_col_name = col
                qualities = qualities.rename(index=str, columns={q_col: q_col_name})

            self._data.update(qualities)

    def read_data_frame_with_comments(self, start: datetime=None, end: datetime=None):
        df = self.read_data_frame(start, end)
        comments = self.get_comments(start, end)
        df['comment'] = pd.Series(['' for i in range(df.shape[0])], index=df.index)
        for i, row in df.iterrows():
            for i_, row_c in comments.iterrows():
                if row_c.loc['from'] <= i <= row_c.loc['until']:
                    df.loc[i, 'comment'] = df.loc[i, 'comment'] + ', ' + row_c['comment'] if df.loc[i, 'comment'] != '' else row_c['comment']
        return df


class CacheStore(TimeSeriesStore):
    def __init__(self, forward: TimeSeriesStore):
        self._forward = forward

    def get_time_series_list(self, ts_filter: str = None, id_list: Iterable[int] = None,
                             params: Mapping[str, Any] = None) -> Iterable[TimeSeries]:
        return [_CacheTimeSeries(ts) for ts in self._forward.get_time_series_list(ts_filter, id_list, params)]

    def get_time_series(self, ts_id: int = None, path: str = None, params: Mapping[str, Any] = None) -> TimeSeries:
        return _CacheTimeSeries(self._forward.get_time_series(ts_id, path, params))

    def write_time_series(self, ts: TimeSeries, start: datetime = None, end: datetime = None,
                          auto_create: bool = False) -> TimeSeries:
        return self._forward.write_time_series(ts, start, end, auto_create)

    def create_time_series(self, path: str, display_name: str, attributes: Mapping = None,
                           params: Mapping[str, Any] = None) -> TimeSeries:
        return self._forward.create_time_series(path, display_name, attributes, params)
