# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Sat Sep  2 12:02:52 2017
# @author: rs

from datetime import datetime
from typing import Iterable, Mapping, MutableMapping

from kisters.water.time_series.time_series import TimeSeries


class TimeSeriesReader:
    def __init__(self, fmt: 'TimeSeriesFormat'):
        self._format = fmt

    def read(self, file: str, metadatahandler: 'TimeSeriesFileMetaDataHandler') -> Iterable[TimeSeries]:
        raise NotImplementedError

    def format(self) -> 'TimeSeriesFormat':
        return self._format


class TimeSeriesWriter:
    def write(self, file: str, time_series_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None):
        raise NotImplementedError


class TimeSeriesFormat:
    def extensions(self) -> Iterable[str]:
        raise NotImplementedError

    def reader(self) -> TimeSeriesReader:
        raise NotImplementedError

    def writer(self) -> TimeSeriesWriter:
        raise NotImplementedError


class TimeSeriesFileMetaDataHandler:
    def read_external_meta_data(self, fmt: TimeSeriesFormat) -> Mapping[str, str]:
        raise NotImplementedError

    def write_external_meta_data(self, fmt: TimeSeriesFormat):
        raise NotImplementedError

    def meta_from_file(self, fmt: TimeSeriesFormat, file: str) -> MutableMapping[str, str]:
        ext_list = fmt.extensions()
        path = file
        for ext in ext_list:
            if file.lower().endswith("." + ext.lower()):
                path = file[:-(len(ext)+1)]
        name = path.split("/")[-1:][0]
        meta = {'tsPath': path, 'name': name, 'shortName': name}
        return meta
