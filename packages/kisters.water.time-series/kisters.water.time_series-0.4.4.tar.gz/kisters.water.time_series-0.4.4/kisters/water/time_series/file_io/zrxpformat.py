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

import datetime
import re
from typing import Iterable, List, Mapping, MutableMapping, TextIO, Union

import numpy as np
from pandas import DataFrame

from kisters.water.time_series.file_io.file_time_series import FileTimeSeries
from kisters.water.time_series.file_io.tsformats import (TimeSeriesFormat, TimeSeriesReader, TimeSeriesWriter,
                                                         TimeSeriesFileMetaDataHandler)
from kisters.water.time_series.time_series import TimeSeries


class ZRXPFormat(TimeSeriesFormat):
    """
    ZRXP formatter class

    Example:
        .. code-block:: python

            from kisters.water.file_io import FileStore, ZRXPFormat
            fs = FileStore('tests/data', ZRXPFormat())
    """
    def extensions(self) -> Iterable[str]:
        return ["zrx", "zrxp"]

    def reader(self) -> TimeSeriesReader:
        return ZRXPReader(self)

    def writer(self) -> TimeSeriesWriter:
        return ZRXPWriter(self)

    @classmethod
    def _header_keys(cls) -> Mapping[str, Union[str, None]]:
        return {"SNAME": "stationName",
                "SANR": "stationNumber",
                "SWATER": "water",
                "CDASA": "dataLogger",
                "CDASANAME": "dataLoggerName",
                "CCHANNEL": "channelName",
                "CCHANNELNO": "channel",
                "CMW": "valuesPerDay",
                "CNAME": "parameterName",
                "CNR": "parameterNumber",
                "CUNIT": "unit",
                "REXCHANGE": "exchangeNumber",
                "RINVAL": "invalidValue",
                "RTIMELVL": "timeLevel",
                "XVLID": "id",
                "TSPATH": "tsPath",
                "CTAG": None,
                "CTAGKEY": None,
                "XTRUNCATE": None,
                "METCODE": None,
                "METERNUMBER": None,
                "EDIS": None,
                "TZ": "timezone",
                "ZDATE": None,
                "ZRXPVERSION": None,
                "ZRXPCREATOR": None,
                "LAYOUT": None,
                "TASKID": None,
                "SOURCESYSTEM": "sourceSystem",
                "SOURCEID": "sourceId"}


class ZRXPReader(TimeSeriesReader):
    def __init__(self, fmt: TimeSeriesFormat=ZRXPFormat(), default_quality: int=200, default_interpolation: int=2):
        TimeSeriesReader.__init__(self, fmt)
        self._default_quality = default_quality
        self._default_interpolation = default_interpolation

    def read(self, file: str,
             metadata_handler: TimeSeriesFileMetaDataHandler=TimeSeriesFileMetaDataHandler()) -> Iterable[TimeSeries]:
        with open(file, 'r') as fh:
            ts_list = []
            ts_data = []
            ts_date = []
            comments = []
            ts_meta = metadata_handler.meta_from_file(self.format(), file)
            state = 'header'
            header_keys = self._format._header_keys()
            ts_list.append(FileTimeSeries(ts_meta, ts_date, ts_data, comments))
            inv = -777.0
            pos_date = 0
            pos_value = 1
            pos_status = None

            for line in fh:
                line = line.strip()
                if len(line) > 0:
                    if line.startswith('##'):
                        comments.append(line)
                    elif line.startswith('#'):
                        if state == 'data':
                            ts_data = []
                            ts_meta = metadata_handler.meta_from_file(self.format(), file)
                            comments = []
                            state = 'header'
                            ts_list.append(FileTimeSeries(ts_meta, ts_data, comments))
                        ts_meta = self._extract_header_line(line[1:], ts_meta, header_keys)
                        if 'RINVAL' in ts_meta:
                            inv = float(ts_meta['RINVAL'])
                        if 'LAYOUT' in ts_meta:
                            layout = self._extract_layout(ts_meta['LAYOUT'])
                            pos_date = layout['timestamp']
                            pos_value = layout['value']
                            if 'status' in layout:
                                pos_status = layout['status']
                            else:
                                pos_status = None

                    else:
                        state = 'data'
                        d = self._extract_data_line(line, inv, pos_date, pos_value, pos_status)
                        ts_date.append(d[0])
                        ts_data.append(d[1])
            return ts_list

    @classmethod
    def _extract_layout(cls, config: str) -> Mapping[str, int]:
        layout = {}
        found = re.search('\\(([^)]+)\\)', config)

        if not found or not found.group(1):
            raise Exception("Invalid layout '{}'".format(config))
        for i in found.group(1).split(","):
            layout[i.strip()] = len(layout)
        if 'timestamp' not in layout:
            raise Exception("Missing timestamp in layout '{}'".format(config))
        if 'value' not in layout:
            raise Exception("Missing value in layout '{}'".format(config))
        return layout

    @classmethod
    def _extract_header_line(cls, line: str, ts_meta: MutableMapping[str, str],
                             header_keys: Mapping[str, str]) -> Mapping[str, str]:
        for i in line.strip().replace(';*;', '|*|').split('|*|'):
            part = i.strip()
            for key, value in header_keys.items():
                if part.startswith(key):
                    ts_meta[key] = part[len(key):]
                    if value is not None:
                        ts_meta[value] = ts_meta[key]
        return ts_meta

    def _extract_data_line(self, line: str, inv: float, pos_date: int, pos_value: int, pos_status: int) -> List:
        blocks = line.split()
        time = datetime.datetime.strptime(blocks[pos_date], '%Y%m%d%H%M%S')
        data = np.double(blocks[pos_value])
        quality = self._default_quality
        if pos_status is not None and len(blocks) > pos_status:
            quality = np.int(blocks[pos_status])
        if data == inv or quality < 0:
            data = None
        return [time, [data, self._default_interpolation, quality]]


class ZRXPWriter(TimeSeriesWriter):
    def __init__(self, fmt: ZRXPFormat=ZRXPFormat()):
        self._format = fmt

    def write(self, file: str, ts_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None):
        with open(file, 'w+') as fh:
            for ts in ts_list:
                self._write_block(fh, ts, start, end)

    def _write_block(self, fh: TextIO, ts: TimeSeries, start: datetime, end: datetime):
        data = ts.read_data_frame(start, end)
        self._write_header(fh, ts, data)
        self._write_data(fh, data)

    def _write_header(self, fh: TextIO, ts: TimeSeries, data: DataFrame):
        fh.write("#" + "|*|".join(self._headervalues(ts)) + "\n")
        if 'value.status' in data.columns.values or 'value.quality' in data.columns.values:
            fh.write("#LAYOUT(timestamp,value,status)|*|\n")

    def _headervalues(self, ts: TimeSeries):
        meta = ts.metadata
        values = ["RINVAL-777"]
        if "tsPath" not in meta:
            values.append("TSPATH" + ts.path)
        for k, v in self._format._header_keys().items():
            if v in meta:
                values.append(k + str(meta[v]))
        return values

    @classmethod
    def _write_data(cls, fh: TextIO, data: DataFrame):
        def nop(fh, row):
            pass
        write_quality = nop
        write_value = nop

        columns = data.columns.values
        for i in range(len(columns) - 1, -1, -1):
            if 'value' == columns[i]:
                cv = columns[i]

                def value(fh, row):
                    fh.write(" ")
                    v = row[cv]
                    if v is None:
                        v = -777
                    fh.write(str(v))
                write_value = value

            if 'quality' in columns[i] or 'status' in columns[i]:
                cq = columns[i]

                def quality(fh, row):
                    fh.write(" ")
                    fh.write(str(int(row[cq])))
                write_quality = quality

        for index, row in data.iterrows():
            fh.write(index.strftime("%Y%m%d%H%M%S"))
            write_value(fh, row)
            write_quality(fh, row)
            fh.write("\n")
        fh.write("\n")
