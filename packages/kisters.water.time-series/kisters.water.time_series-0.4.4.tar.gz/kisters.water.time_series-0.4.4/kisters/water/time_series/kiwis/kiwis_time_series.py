# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Tue Nov 21 11:04:35 2017
# @author: mrd

import pprint
import re
from requests import Response
from datetime import datetime
from typing import Any, Dict, Mapping, Optional

import dateutil
import pandas as pd
from pandas import DataFrame

from kisters.water.time_series.kiwis.helpers import prepare_params
from kisters.water.time_series.time_series import TimeSeries
from kisters.water.time_series.time_series_store import TimeSeriesStore
from kisters.water.time_series.time_series_attributes_mixin import TimeSeriesAttributesMixin
from kisters.water.time_series.time_series_cut_range_mixin import TimeSeriesCutRangeMixin
from kisters.water.time_series.time_series_item_mixin import TimeSeriesItemMixin


pp = pprint.PrettyPrinter(indent=4)


class _KiWISTimeSeries(TimeSeriesItemMixin, TimeSeriesAttributesMixin, TimeSeriesCutRangeMixin, TimeSeries):
    """ KiWIS REST specific time series implementation
    """

    def __init__(self, kiwis: TimeSeriesStore, j: Dict[str, Any], init_coverage: bool=True):
        j['tsPath'] = j.pop('ts_path', None)
        j['shortName'] = j.pop('ts_shortname', None)
        self.__dict__ = j.copy()
        super(_KiWISTimeSeries, self).__init__()
        self._kiwis = kiwis
        self._metadata = j.copy()

        if "from" in j and j["from"] != "":
            self._metadata["from"] = dateutil.parser.parse(j["from"])
        if "to" in j and j["to"] != "":
            self._metadata["to"] = dateutil.parser.parse(j["to"])

        self.__init_coverage = init_coverage

    def _raw_metadata(self) -> Mapping[str, Any]:
        return self._metadata

    def _data(self, start: datetime=None, end: datetime=None, params: Mapping[str, Any]=None) -> Response:
        if params is None:
            params = {}

        if start is not None:
            params["from"] = start.isoformat()
        else:
            params["from"] = self.coverage_from.isoformat()

        if end is not None:
            params["to"] = end.isoformat()
        else:
            params["to"] = self.coverage_until.isoformat()

        if self.path is not None:
            params["ts_path"] = self.path
        else:
            params["ts_id"] = self._metadata["id"]

        params = prepare_params(params)

        # pylint: disable=protected-access
        j = self._kiwis._get("getTimeseriesValues", params=params)
        # pylint: enable=protected-access
        return j

    def _load_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping[str, Any]=None) -> DataFrame:
        data = self._data(start, end, params)
        j = data.json()[0]
        c = j["columns"].split(',')
        d = j["data"]
        ts_col = 'timestamp'
        c[0] = ts_col
        raw_data = DataFrame(d, columns=c)
        raw_data[ts_col] = pd.to_datetime(raw_data[ts_col], utc=True)
        raw_data.set_index(ts_col)
        raw_data.index = raw_data[ts_col]
        return raw_data[c[1:]]

    @property
    def coverage_from(self) -> Optional[datetime]:
        if 'from' not in self._metadata:
            self._init_coverage()
            if 'from' not in self._metadata:
                return None
        return self._metadata["from"]

    @property
    def coverage_until(self) -> Optional[datetime]:
        if 'to' not in self._metadata:
            self._init_coverage()
            if 'to' not in self._metadata:
                return None
        return self._metadata["to"]

    def _init_coverage(self):
        if self.__init_coverage:
            self.__init_coverage = False
            ts = self._kiwis.get_time_series(self._metadata["id"])
            self._metadata['from'] = ts.coverage_from
            self._metadata['to'] = ts.coverage_until

    def transform(self, transformation: str) -> TimeSeries:
        if re.match(".*\\(.*\\)", self.path):
            return self._kiwis.get_time_series(path=self.path + ";" + transformation)
        else:
            return self._kiwis.get_time_series(path="tsm(" + self.path + ");" + transformation)

    def get_comments(self, start: datetime = None, end: datetime = None) -> DataFrame:
        """ Read comments from a time series and returns it as data frame

        :param start: optional start time stamp
        :param end: optional end time stamp
        """
        return self.read_data_frame(start=start, end=end, params={
            'returnfields': ['Timestamp', 'Timeseries Comment', 'Agent Comment', 'Station Comment', 'Parameter Comment',
                             'Data Comment']
        })

    def write_data_frame(self, data_frame, start: datetime=None, end: datetime=None, default_quality=200, default_interpolation=1):
        self._to_data(data_frame)

    def _to_data(self, data_frame, default_quality=200, default_interpolation=1):
        raise NotImplementedError
