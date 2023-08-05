# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Sat Sep  2 12:03:48 2017
# @author: rs

from datetime import datetime
from typing import Mapping, Union

from pandas import DataFrame

from kisters.water.time_series.time_series import TimeSeries
from kisters.water.time_series.time_series_attributes_mixin import TimeSeriesAttributesMixin
from kisters.water.time_series.time_series_cut_range_mixin import TimeSeriesCutRangeMixin
from kisters.water.time_series.time_series_item_mixin import TimeSeriesItemMixin


class TimeSeriesDecorator(TimeSeriesItemMixin, TimeSeriesAttributesMixin, TimeSeriesCutRangeMixin, TimeSeries):
    def __init__(self, forward: Union[TimeSeries, TimeSeriesCutRangeMixin]):
        super().__init__()
        self._forward = forward

    def _raw_metadata(self) -> Mapping:
        return self._forward.metadata

    def _load_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping=None) -> DataFrame:
        return self._forward._load_data_frame(start, end, params)

    @property
    def coverage_from(self) -> datetime:
        return self._forward.coverage_from

    @property
    def coverage_until(self) -> datetime:
        return self._forward.coverage_until

    def write_data_frame(self, data_frame: DataFrame):
        return self._forward.write_data_frame(data_frame)
