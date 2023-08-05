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

import csv
from csv import DictWriter
from datetime import datetime
from dateutil import parser
from typing import Any, Callable, Iterable, Tuple, Mapping, TextIO

import numpy as np
from pandas import DataFrame

from kisters.water.time_series.file_io.file_time_series import FileTimeSeries
from kisters.water.time_series.file_io.tsformats import (TimeSeriesFormat, TimeSeriesReader, TimeSeriesWriter,
                                                         TimeSeriesFileMetaDataHandler)
from kisters.water.time_series.time_series import TimeSeries


def reader(file: TextIO, delimiter: str, quotechar: str):
    return csv.reader(file, delimiter=delimiter, quotechar=quotechar)


def writer(file: TextIO, delimiter: str, quotechar: str) -> DictWriter:
    w = csv.writer(file, delimiter=delimiter, quotechar=quotechar, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    return w


class CSVFormat(TimeSeriesFormat):
    """
    CSV formatter class

    Example:
        .. code-block:: python

            from kisters.water.file_io import FileStore, CSVFormat
            fs = FileStore('tests/data', CSVFormat())
    """
    def __init__(self, delimiter: str=',', quotechar: str='"', reader: Callable=reader, writer: Callable=writer):
        self._delimiter = delimiter
        self._quotechar = quotechar
        self._reader = reader
        self._writer = writer

    def extensions(self) -> Iterable[str]:
        return ["csv"]

    def reader(self) -> TimeSeriesReader:
        return CSVReader(self, self._reader)

    def writer(self) -> TimeSeriesWriter:
        return CSVWriter(self, self._writer)


class CSVReader(TimeSeriesReader):
    def __init__(self, fmt: TimeSeriesFormat=CSVFormat(), reader: Callable=None):
        TimeSeriesReader.__init__(self, fmt)
        self._reader = reader
        if reader is not None:
            self._reader = reader

    def read(self, file: str,
             metadata_handler: TimeSeriesFileMetaDataHandler=TimeSeriesFileMetaDataHandler()) -> Iterable[str]:
        with open(file, 'r') as fh:
            time_series_list = []
            tsdata = []
            tsdate = []
            comments = []
            tsmeta = metadata_handler.meta_from_file(self.format(), file)
            state = 'header'
            time_series_list.append(FileTimeSeries(tsmeta, tsdate, tsdata, comments))

            reader = self._reader(fh, delimiter=self._format._delimiter, quotechar=self._format._quotechar)

            for row in reader:
                if state == 'header':
                    state = 'data'
                else:
                    tsdate.append(parser.parse(row[0]))
                    if len(row) < 2 or len(row[1]) == 0:
                        tsdata.append(None)
                    else:
                        tsdata.append(float(row[1]))
            return time_series_list

    @classmethod
    def _extract_header_line(cls, tsmeta: Mapping[str, Any]) -> Mapping[str, Any]:
        return tsmeta

    @classmethod
    def _extract_data_line(cls, line: str, inv: float) -> Tuple[datetime, float]:
        blocks = line.split(' ')
        time = datetime.strptime(blocks[0], '%Y%m%d%H%M%S')
        data = np.double(blocks[1])
        if data == inv:
            data = None
        return time, data


class CSVWriter(TimeSeriesWriter):
    def __init__(self, fmt: CSVFormat=CSVFormat(), writer: Callable=None):
        self._format = fmt
        self._writer = writer
        if writer is not None:
            self._writer = writer

    def write(self, file: str, time_series_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None):
        with open(file, 'w') as fh:
            for ts in time_series_list:
                self._write_block(fh, ts, start, end)
                break

    def _write_block(self, fh: TextIO, ts: TimeSeries, start: datetime, end: datetime):
        data = ts.read_data_frame(start, end)
        writer = self._writer(fh, delimiter=self._format._delimiter, quotechar=self._format._quotechar)
        self._write_header(writer)
        self._write_data(writer, data)

    @classmethod
    def _write_header(cls, writer: DictWriter):
        writer.writerow(["timestamp", "value"])

    @classmethod
    def _write_data(cls, writer: DictWriter, data: DataFrame):
        for index, row in data.iterrows():
            writer.writerow([index, row['value']])
