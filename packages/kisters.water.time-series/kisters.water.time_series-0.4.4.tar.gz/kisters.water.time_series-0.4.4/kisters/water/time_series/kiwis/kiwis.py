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
import itertools
import logging
from typing import Any, Iterable, Mapping, List

import requests

from kisters.water.time_series.kiwis.helpers import prepare_params
from kisters.water.time_series.kiwis.kiwis_time_series import _KiWISTimeSeries
from kisters.water.time_series import TimeSeries, TimeSeriesStore

logger = logging.getLogger(__name__)


class KiWISStore(TimeSeriesStore):
    """Connector to KiWIS backend over KiWIS REST API

    Args:
        base_url: Base url of REST API.
        data_source: Optional number identifying the data source.

    Examples:
        .. code-block:: python

            kiwis = KiWISStore('http://kiwis.kisters.de/KiWIS2/KiWIS')
            kiwis.get_by_path('DWD/07367/Precip/CmdTotal.1h')
    """

    def __init__(self, base_url: str, data_source: int=None):
        self._rest_url = base_url
        self.__data_source = data_source
        self.__service = 'kisters'
        self.__type = 'queryServices'

    def change_data_source(self, data_source: int=None):
        self.__data_source = data_source

    def _get(self, req: str, accept: str = "application/json",
             params: Mapping[str, Any] = None) -> requests.Response:
        url = self._rest_url

        header = {'Accept': accept}

        params['datasource'] = self.__data_source
        params['service'] = self.__service
        params['type'] = self.__type
        params['request'] = req

        if accept is "application/json":
            params['format'] = 'json'
        elif accept is "text/html":
            params['format'] = 'html'
        else:
            params['format'] = 'json'

        response = requests.get(url, headers=header, params=params)

        if response.status_code == 403 or response.status_code == 401:
            header = {
                'Accept': accept,
            }
            response = requests.get(url, headers=header, params=params)

        if not response.ok:
            logger.debug(url)
            logger.debug(str(header))
            raise response.raise_for_status()
        return response

    def get_time_series_list(self, ts_filter: str = None,
                             id_list: Iterable[int] = None, params: Mapping[str, Any] = None) -> List[TimeSeries]:
        """Get the time series list and return a list of TimeSeries objects

        Args:
            ts_filter: The ts filter.
            id_list: The id list.
            params: The additional parameters, which are passed to rest api
                    in addition to the parameters defined by the REST API there
                    are the following keys:
                        metadata = comma separated list of additional meta information
                                   where the values are "site", "station", "parameter".

        Returns:
             The list of TimeSeries objects.

        Examples:
            .. code-block:: python
                kiwis.get_time_series_list(ts_filter = "FR110031fb-e8e7-4381-a942-372aa8141945/CM0514*")
                kiwis.get_time_series_list(id_list = 40765010)
                kiwis.get_time_series_list(id_list = 40765010, params = {"includeParent": True})
        """
        if params is None:
            params = {}

        if id_list is not None:
            params["ts_id"] = id_list
        if ts_filter is not None:
            params["ts_path"] = ts_filter

        params.setdefault('returnfields', ['ts_id', 'ts_name', 'ts_path', 'ts_shortname'])
        params['returnfields'].append('coverage')

        params, metakeys = self._add_metadata_params(params)
        params = prepare_params(params)
        ts_list = []

        j = self._get("getTimeseriesList", params=params).json()
        keys = j[0]
        for ts in j[1:]:
            m = dict(zip(keys, ts))
            ts_list.append(_KiWISTimeSeries(self, m))
        self._merge_metadata(ts_list, metakeys)
        return ts_list

    @classmethod
    def _add_metadata_params(cls, params: Mapping[str, Any] = None) -> (Mapping[str, Any], List[str]):
        if params is None:
            result_params = {}
        else:
            result_params = params.copy()

        result_params.setdefault('returnfields', {})

        metakeys = result_params['metadata'] if 'metadata' in result_params else []
        metadata = list(itertools.chain.from_iterable(map(cls._convert_metadata, metakeys)))

        result_params['returnfields'] = result_params['returnfields'] + metadata
        if 'metadata' in result_params:
            del result_params['metadata']

        return result_params, ','.join(metadata).split(',')

    @classmethod
    def _convert_metadata(cls, s: str) -> List[str]:
        all_lookup_table = {
            'station':
                ['station_no', 'station_id', 'station_name', 'station_latitude', 'station_longitude',
                 'station_carteasting', 'station_cartnorthing', 'station_local_x', 'station_local_y',
                 'station_georefsystem', 'station_longname'],
            'parametertype':
                ['parametertype_id', 'parametertype_name'],
            'stationparameter':
                ['stationparameter_name', 'stationparameter_no', 'stationparameter_longname'],
            'site':
                ['site_no', 'site_id', 'site_name'],
            'catchment':
                ['catchment_no', 'catchment_id', 'catchment_name'],
            'ts':
                ['ts_id', 'ts_name', 'ts_shortname', 'ts_path', 'ts_type_id', 'ts_type_name', 'ts_unitname',
                 'ts_unitsymbol', 'ts_unitname_abs', 'ts_unitsymbol_abs']
        }
        if s.endswith('.all'):
            return all_lookup_table[s.split('.')[0]]
        elif '.' in s:
            return [s.replace('.', '_')]
        else:
            return ['ts_' + s]

    def _merge_metadata(self, ts_list: Iterable[_KiWISTimeSeries], metadata: List[str]):
        for ts in ts_list:
            meta_dict = ts._raw_metadata()

            for key in metadata:
                if '_' not in key:
                    continue
                i = key.index('_')
                bd_type = key[0:i]
                bd_key = key[i + 1:]
                if bd_type == 'ts':
                    meta_dict[bd_key] = meta_dict.pop(key)
                else:
                    if bd_type not in meta_dict:
                        meta_dict[bd_type] = {}

                    meta_dict[bd_type][bd_key] = meta_dict.pop(key)

            meta_dict['id'] = int(meta_dict.pop('ts_id'))
            meta_dict['name'] = meta_dict.pop('ts_name')

    def get_time_series(self, ts_id: int = None, path: str = None, params: Mapping[str, Any] = None) -> TimeSeries:
        """Get a time series identified by id or by path and return a TimeSeries

        Args:
            ts_id: The time series id.
            path: The time series path (ignored if ts_id is given).
            params: The additional parameters, which are passed to the rest api.
                    in addition to the parameters defined by the REST API there
                    are the following keys:
                        metadata = comma separated list of additional meta information
                                   where the values are "site", "station", "parameter"
                    params['metadata'] is a string with a comma separated list of additional meta data.
                    All time series specific information should be specified as is. All station,
                    site and parameter specific information should be prefixed with "station." etc.

        Returns:
             The found TimeSeries object.

        Examples:
            .. code-block:: python
                kiwis.get_time_series(ts_id = 40765010)

            There is a special key 'all' which allows to retrieve all metadata keys of the specified object.
            But this should be handeld with care, because it is expensive.
                ts = self.kiwis.get_time_series(ts_id=40765010, params={'metadata': 'station.all'})

            The following statement would retrieve all available information:
                kiwis.get_time_series(ts_id=40765010, params={'metadata': 'all,parameter.all,station.all,site.all'})

        """

        res = self.get_time_series_list(ts_filter=path, id_list=[ts_id] if ts_id is not None else None, params=params)
        if len(res) != 1:
            raise KeyError('Requested TimeSeries does not exist.')
        return res[0]

    def create_time_series(self, path: str, display_name: str, attributes: Mapping = None,
                           params: Mapping = None) -> TimeSeries:
        raise NotImplementedError

    def write_time_series(self, ts, start=None, end=None, auto_create=False):
        raise NotImplementedError
