# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, KISTERS AG, Germany.
# All rights reserved.
# Modification, redistribution and use in source and binary
# forms, with or without modification, are not permitted
# without prior written approval by the copyright holder.
#
# Created on Sat Sep  2 12:38:39 2017
# @author: rs

from datetime import datetime, date
from dateutil import parser
import json
import os
import re
from typing import Any, Iterable, List, Mapping, Union

from pandas import DataFrame
from pandas.compat import FileNotFoundError

from kisters.water.time_series.file_io.file_time_series import FileTimeSeries
from kisters.water.time_series.file_io.tsformats import TimeSeriesFileMetaDataHandler, TimeSeriesFormat
from kisters.water.time_series import TimeSeries, TimeSeriesStore, TimeSeriesDecorator


class AddMetadataStore(TimeSeriesStore):
    """
    AddMetadataStore is a TimeSeriesStore decorator which allows to add metadata
    to TimeSeries inside the original TimeSeriesStore. To add metadata you must
    provide a Mapping of paths to metadata dictionaries.

    Args:
        forward: The TimeSeriesStore to be decorated.
        metadata: The mapping providing metadata. Keys are the time series paths,
                  and values are the metadata maps for each time series.

    Example:
        .. code-block:: python

            import json
            from kisters.water.file_io import AddMetadataStore, FileStore, ZRXPFormat
            with open('tests/data/addmetadata.json', 'r') as f:
                j = json.load(f)
            store = AddMetadataStore(FileStore('tests/data', ZRXPFormat()), j)
            ts = store.get_by_path('validation/threshold/05BJ004.HG.datum.O')
            ts.metadata['THRESHOLDATTR']
    """

    def __init__(self, forward: TimeSeriesStore, metadata: Mapping[str, Any]):
        self._forward = forward
        self._metadata = metadata

    def create_time_series(self, path: str, display_name: str, attributes: Mapping[str, Any]=None,
                           params: Mapping=None) -> TimeSeries:
        raise NotImplementedError

    def get_time_series_list(self, ts_filter: str=None, id_list: List[int]=None,
                             params: Mapping=None) -> Iterable[TimeSeries]:
        ts_list = self._forward.get_time_series_list(ts_filter, id_list, params)
        ts_list = [AddMetadataTimeSeries(self, ts) for ts in ts_list]
        return ts_list

    def get_time_series(self, ts_id: int=None, path: str=None, params: Mapping[str, Any]=None) -> TimeSeries:
        ts = AddMetadataTimeSeries(self, self._forward.get_time_series(ts_id, path, params))
        return ts

    def write_time_series(self, ts: TimeSeries, start: datetime = None, end: datetime = None,
                          auto_create: bool = False) -> TimeSeries:
        raise NotImplementedError

    def lookup_metadata(self, path: str) -> Union[Mapping[str, Any], None]:
        if path in self._metadata:
            return self._metadata[path]
        return None


class AddMetadataTimeSeries(TimeSeriesDecorator):
    def __init__(self, backend: AddMetadataStore, ts: TimeSeries):
        super().__init__(ts)
        self._backend = backend

    def _raw_metadata(self):
        meta = self._backend.lookup_metadata(self._forward.path)
        if meta is None:
            meta = {}
        else:
            meta = meta.copy()
        meta.update(self._forward.metadata)
        return meta


class MetaDataHandler(TimeSeriesFileMetaDataHandler):
    def __init__(self, root_dir: str, file_format: TimeSeriesFormat):
        self._root_dir = root_dir
        self._file_format = file_format

    @classmethod
    def write_time_series_list(cls, file: str, ts_list: Iterable[TimeSeries]):
        metalist = []
        for ts in ts_list:
            metalist.append(ts.metadata)
        with open(file + ".metadata", "w") as o:
            json.dump(
                metalist, o, default=_json_serial, indent=4, sort_keys=True)

    def get_time_series_list(self, file: str) -> Union[Iterable[TimeSeries], None]:
        if not os.path.isfile(file + ".metadata"):
            return None
        ts_list = []
        with open(file + ".metadata", "r") as r:
            j = json.load(r)
            index = 0
            filereader = MetaDataTimeSeriesReader(self, file)
            for ts in j:
                ts_list.append(MetaDataTimeSeries(self, ts, index, filereader))
                index = index + 1
        return ts_list

    def meta_from_file(self, fmt: TimeSeriesFormat, file: str) -> Mapping[str, Any]:
        ext_list = fmt.extensions()
        path = file
        for ext in ext_list:
            if file.lower().endswith("." + ext.lower()):
                path = file[:-(len(ext) + 1)]
        if path.startswith(self._root_dir + "/"):
            path = path[(len(self._root_dir) + 1):]
        name = path.split("/")[-1:][0]
        meta = {'tsPath': path, 'name': name, 'shortName': name}
        return meta

    def write_external_meta_data(self, fmt):
        raise NotImplementedError

    def read_external_meta_data(self, fmt):
        raise NotImplementedError


class MetaDataTimeSeriesReader:
    def __init__(self, handler: MetaDataHandler, file: str):
        self._ts_list = None
        self._reader = handler._file_format.reader()
        self._file = file
        self._handler = handler

    def ts(self, index: int) -> TimeSeries:
        if self._ts_list is None:
            self._ts_list = self._reader.read(self._file, self._handler)
        return list(self._ts_list)[index]


class MetaDataTimeSeries(FileTimeSeries):
    def __init__(self, handler: MetaDataHandler, j: Mapping[str, Any], index: int, reader: MetaDataTimeSeriesReader):
        self.__dict__ = j.copy()
        super().__init__()
        self._handler = handler
        self._reader = reader
        self._file_ts = None
        self._index = index
        self._meta = j.copy()
        if "dataCoverageFrom" in j:
            self._meta["dataCoverageFrom"] = parser.parse(
                j["dataCoverageFrom"])
        if "dataCoverageUntil" in j:
            self._meta["dataCoverageUntil"] = parser.parse(
                j["dataCoverageUntil"])

    def _ts(self) -> TimeSeries:
        if self._file_ts is None:
            self._file_ts = self._reader.ts(self._index)
        return self._file_ts

    def _raw_metadata(self) -> Mapping[str, Any]:
        return self._meta

    @property
    def coverage_from(self) -> datetime:
        if 'dataCoverageFrom' in self._meta:
            return self._meta['dataCoverageFrom']
        return self._ts().coverage_from

    @property
    def coverage_until(self) -> datetime:
        if 'dataCoverageUntil' in self._meta:
            return self._meta['dataCoverageUntil']
        return self._ts().coverage_until

    def _load_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping[str, Any]=None) -> DataFrame:
        return self._ts()._load_data_frame(start, end, params)

    def write_data_frame(self, data_frame: DataFrame):
        raise NotImplementedError


def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        iso = obj.isoformat()
        if obj.utcoffset() is None:
            iso += "Z"
        return iso
    return str(obj)


class FileStore(TimeSeriesStore):
    """FileStore provides a TimeSeriesStore for your local time series data files

    Args:
        root_dir: The path to your time series data folder.
        file_format: The format used by your time series data files.
        metadata_handler: Not required. It uses a MetaDataHandler per default, this extracts
                          time series metadata into a separate file which can be modified and
                          is used by the FileStore to retrieve time series meta data.

    Examples:
        .. code-block:: python

            from kisters.water.file_io import FileStore, ZRXPFormat
            fs = FileStore('tests/data', ZRXPFormat())
            ts = fs.get_by_path('validation/inner_consistency1/station1/H')
    """
    def __init__(self, root_dir: str, file_format: TimeSeriesFormat, metadata_handler: MetaDataHandler=None):
        self._metadata_handler = metadata_handler
        if self._metadata_handler is None:
            self._metadata_handler = MetaDataHandler(root_dir, file_format)
        self._file_format = file_format
        self._root_dir = root_dir
        if not os.path.isdir(self._root_dir):
            raise FileNotFoundError(
                "Path " + os.path.abspath(self._root_dir) + " does not exist")

    def create_time_series(self, path: str, display_name: str, attributes: Mapping[str, Any]=None,
                           params: Mapping[str, Any]=None) -> TimeSeries:
        raise NotImplementedError

    def get_time_series_list(self, ts_filter: str=None, id_list: List[int]=None,
                             params: Mapping[str, Any]=None) -> Iterable[TimeSeries]:
        ts_list = []
        for f in self._file_list(self._root_dir):
            meta_list = self._metadata_handler.get_time_series_list(f)
            if meta_list is not None:
                for m in meta_list:
                    ts_list.append(m)
            else:
                sublist = self._file_format.reader().read(
                    f, self._metadata_handler)
                self._metadata_handler.write_time_series_list(f, sublist)
                for ts in sublist:
                    ts_list.append(ts)
        ts_list = self._filter(ts_list, ts_filter)
        ts_list = self._filter_id_list(ts_list, id_list)
        return ts_list

    @classmethod
    def _filter(cls, ts_list: Iterable[TimeSeries], ts_filter: str) -> Iterable[TimeSeries]:
        if ts_filter is None:
            return ts_list
        result = []
        exp = re.compile(ts_filter.replace(".", "\\.").replace(
            "/", "\\/").replace("?", "\\?").replace("*", ".*"))
        for ts in ts_list:
            path = ts.path
            if exp.match(path):
                result.append(ts)
        return result

    @classmethod
    def _filter_id_list(cls, ts_list: Iterable[TimeSeries], id_list: Iterable[int]) -> Iterable[TimeSeries]:
        if id_list is None:
            return ts_list
        result = []
        for ts in ts_list:
            ts_id = ts.id
            if (ts_id is not None) and (ts_id in id_list):
                result.append(ts)
        return result

    def get_time_series(self, ts_id: int=None, path: str=None,
                        params: Mapping[str, Any]=None) -> Union[TimeSeries, None]:
        if params is None:
            params = {"includeDataCoverage": True}
        ts_list = list(self.get_time_series_list(
            ts_filter=path, id_list=[ts_id] if ts_id else None, params=params))
        if len(ts_list) == 0:
            raise KeyError('Requested TimeSeries does not exist.')
        else:
            return ts_list[0]

    def _file_list(self, path: str) -> List[str]:
        file_list = []
        try:
            extensions = self._file_format.extensions()
            for f in os.listdir(path):
                if os.path.isfile(path + "/" + f):
                    for e in extensions:
                        if f.lower().endswith("." + e.lower()):
                            file_list.append(path + "/" + f)
                elif os.path.isdir(path + "/" + f):
                    for ff in self._file_list(path + "/" + f):
                        file_list.append(ff)
        except:
            # TODO catch adecuate exceptions
            return file_list
        return file_list

    def write_time_series_list(self, ts_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None,
                               auto_create: bool=False):
        for ts in ts_list:
            self.write_time_series(ts, start, end)

    def write_time_series(self, ts: TimeSeries, start: datetime=None, end: datetime=None, auto_create: bool=False):
        parents = ts.path.split("/")
        path = self._root_dir
        if not os.path.isdir(path):
            os.mkdir(path)
        if len(parents) > 0:
            for p in parents[:-1]:
                path = path + "/" + p
                if not os.path.isdir(path):
                    os.mkdir(path)
        file = self._root_dir + "/" + ts.path + "." + list(self._file_format.extensions())[0]
        writer = self._file_format.writer()
        writer.write(file, [ts], start, end)
        self._metadata_handler.write_time_series_list(file, [ts])
