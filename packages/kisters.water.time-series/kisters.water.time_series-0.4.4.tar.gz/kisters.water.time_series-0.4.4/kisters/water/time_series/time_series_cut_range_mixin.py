# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on 13.02.2018
# @author: rs

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from tzlocal import get_localzone
import pytz
from typing import Mapping, Union

from pandas import DataFrame, to_datetime


class TimeSeriesCutRangeMixin(ABC):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(TimeSeriesCutRangeMixin, self).__init__()
        self._tz = pytz.utc

    @abstractmethod
    def _load_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping=None) -> DataFrame:
        pass

    def _get_timezone(self) -> pytz.timezone:
        return self._tz

    def _to_zoned_datetime(self, dt: Union[str, datetime]) -> Union[datetime, None]:
        if dt is None:
            return None
        else:
            return to_datetime(dt, utc=True).tz_convert(self._get_timezone())

    def read_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping=None) -> DataFrame:
        start = self._to_zoned_datetime(start)
        end = self._to_zoned_datetime(end)

        df = self._load_data_frame(start, end, params)
        df.index = df.index.tz_convert(self._get_timezone())
        return df
