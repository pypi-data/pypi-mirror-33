# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Sat Sep  2 12:13:16 2017
# @author: rs

from datetime import datetime
from typing import Iterable

import pandas as pd

from kisters.water.time_series.file_io.file_time_series import FileTimeSeries
from kisters.water.time_series.file_io.tsformats import (TimeSeriesFormat, TimeSeriesReader, TimeSeriesWriter,
                                                         TimeSeriesFileMetaDataHandler)
from kisters.water.time_series import TimeSeries


class PickleFormat(TimeSeriesFormat):
    """
    Pickle formatter class

    Example:
        .. code-block:: python
        
            from kisters.water.file_io import FileStore, PickleFormat
            fs = FileStore('tests/data', PickleFormat())
    """
    def extensions(self) -> Iterable[str]:
        return ["pkl"]

    def reader(self) -> TimeSeriesReader:
        return PickleReader(self)

    def writer(self) -> TimeSeriesWriter:
        return PickleWriter(self)


class PickleReader(TimeSeriesReader):
    def __init__(self, fmt: TimeSeriesFormat=PickleFormat()):
        TimeSeriesReader.__init__(self, fmt)

    def read(self, file: str,
             metadatahandler: TimeSeriesFileMetaDataHandler=TimeSeriesFileMetaDataHandler()) -> Iterable[TimeSeries]:
        df = pd.read_pickle(file)
        ts_meta = metadatahandler.meta_from_file(self.format(), file)
        ts = FileTimeSeries(ts_meta, df.index, df.values, None)
        return [ts]


class PickleWriter(TimeSeriesWriter):
    def __init__(self, fmt: TimeSeriesFormat=PickleFormat()):
        self._format = fmt

    def write(self, file: str, time_series_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None):
        list(time_series_list)[0].read_data_frame(start, end).to_pickle(file)
