# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Tue Aug 29 16:29:26 2017
# @author: rs

from datetime import datetime
import logging
from typing import Iterable, Mapping, Union

import numpy as np
from pandas import DataFrame, to_datetime

from kisters.water.time_series.time_series import TimeSeries
from kisters.water.time_series.time_series_attributes_mixin import TimeSeriesAttributesMixin
from kisters.water.time_series.time_series_cut_range_mixin import TimeSeriesCutRangeMixin
from kisters.water.time_series.time_series_item_mixin import TimeSeriesItemMixin


logger = logging.getLogger(__name__)


class FileTimeSeries(TimeSeriesItemMixin, TimeSeriesAttributesMixin, TimeSeriesCutRangeMixin, TimeSeries):
    def __init__(self, meta: Mapping[str, str]=None, time: Iterable[datetime]=None, data: Iterable[np.double]=None,
                 comments: Iterable[str]=None):
        super().__init__()
        self._meta = meta
        self._time = time
        self._data = data
        self._comments = comments

    @property
    def coverage_from(self) -> Union[datetime, None]:
        time_list = list(self._time)
        if self._time is None or len(time_list) == 0:
            return None
        return time_list[0]

    @property
    def coverage_until(self) -> Union[datetime, None]:
        time_list = list(self._time)
        if self._time is None or len(time_list) == 0:
            return None
        return time_list[-1]

    def _raw_metadata(self) -> Mapping[str, str]:
        return self._meta

    def _load_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping[str, str]=None) -> DataFrame:
        if len(list(self._data)) == 0 or (isinstance(self._data[0], (list, np.ndarray)) and len(self._data[0]) == 3):
            df = DataFrame(self._data, index=to_datetime(self._time, utc=True),
                           columns=['value', 'value.interpolation', 'value.quality'])
        else:
            df = DataFrame(self._data, index=to_datetime(self._time, utc=True), columns=['value'])
        if start is None and end is None:
            return df
        if start is None:
            mask = df.index <= end
        elif end is None:
            mask = df.index >= start
        else:
            mask = (df.index >= start) & (df.index <= end)
        return df.loc[mask]

    @classmethod
    def write_comments(cls, comments):
        logger.warning("write_comments not implemented. Ignoring {} comments".format(len(comments)))

    @classmethod
    def update_qualities(cls, qualities):
        logger.warning("update_qualities not implemented. Ignoring {} qualities".format(len(qualities)))

    def write_data_frame(self, data_frame: DataFrame):
        raise NotImplementedError
