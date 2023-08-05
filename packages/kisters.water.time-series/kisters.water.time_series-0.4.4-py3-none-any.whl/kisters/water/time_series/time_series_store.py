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

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, Mapping, Union

from kisters.water.time_series.time_series import TimeSeries


def deprecated(funcobj):
    return funcobj


class TimeSeriesStore(ABC):
    def get_by_id(self, ts_id: Union[int, Iterable[int]],
                  params: Mapping[str, Any]=None) -> Union[TimeSeries, Iterable[TimeSeries]]:
        """Get the time series by id.

        Args:
            ts_id: List of ids or single id.
            params: The additional parameters, which are passed to the backend.

        Returns:
            The time series or a list of time series if ts_id is a list.

        Examples:
            .. code-block:: python

                store.get_by_id(4711)
                store.get_by_id([4711, 4712])

        """
        if isinstance(ts_id, int):
            return self.get_time_series(ts_id=ts_id, params=params)
        else:
            return self.get_time_series_list(id_list=ts_id, params=params)

    def get_by_path(self, path: str, params: Mapping[str, Any]=None) -> TimeSeries:
        """Get the time series by path.

        Args:
            path: The full qualified time series path.
            params: The additional parameters, which are passed to the backend.

        Returns:
            The TimeSeries object.

        Examples:
            .. code-block:: python

                store.get_by_path("W7AgentTest/20003/S/cmd")

        """
        if path[0] == '/':
            raise ValueError('Unexpected leading slash in path, use {}'.format(path[1:]))
        return self.get_time_series(path=path, params=params)

    def get_by_filter(self, ts_filter: str, params: Mapping[str, Any]=None) -> Iterable[TimeSeries]:
        """Get the time series list by filter.

        Args:
            ts_filter: time series path or filter.
            params: the additional parameters, which are passed to the backend.

        Returns:
            The list of the found TimeSeries objects.

        Examples:
            .. code-block:: python

                store.get_by_filter("W7AgentTest/20004/S/*")
        """
        if ts_filter[0] == '/':
            raise ValueError('Unexpected leading slash in path, use {}'.format(ts_filter[1:]))
        return self.get_time_series_list(ts_filter=ts_filter, params=params)

    @deprecated
    @abstractmethod
    def get_time_series_list(self, ts_filter: str=None, id_list: Iterable[int]=None,
                             params: Mapping[str, Any]=None) -> Iterable[TimeSeries]:
        """
        Deprecated: 0.3.0
            Use :func:`get_by_filter` or :func:`get_by_id`.

        Get the time series list and return a list of TimeSeries objects.

        Args:
            ts_filter: The ts filter.
            id_list: The id list.
            params: The additional parameters, which are passed to the backend.

        Returns:
             The list of TimeSeries objects.

        """
        pass

    @deprecated
    @abstractmethod
    def get_time_series(self, ts_id: int=None, path: str=None, params: Mapping[str, Any]=None) -> TimeSeries:
        """
        Deprecated: 0.3.0
            Use :func:`get_by_path` or :func:`get_by_id`.

        Get a time series identified by id or by path and return a TimeSeries.

        Args:
            ts_id: The time series id.
            path: The time series path.
            params: The additional parameters, which are passed to the backend.

        Returns:
             The TimeSeries objects.
        """
        pass

    def write_time_series_list(self, ts_list: Iterable[TimeSeries], start: datetime=None, end: datetime=None,
                               auto_create: bool=False):
        """Write a time series list to the back end for the given time range.

        Args:
            ts_list: The time series list.
            start: The starting date from which data will be written.
            end: The ending date until which data will be written.
            auto_create: Create the time series if not exists in the back end.

        Examples:
            .. code-block:: python

                ts_list = store1.get_by_filter('W7AgentTest/2000*')
                store2.write_time_series_list(ts_list, datetime(2001, 1, 1), datetime(2002, 1, 1))

        """
        for ts in ts_list:
            self.write_time_series(ts, start, end, auto_create)

    @abstractmethod
    def write_time_series(self, ts: TimeSeries, start: datetime=None, end: datetime=None,
                          auto_create: bool=False) -> TimeSeries:
        """Write a single time series to the time series back end for the given time range.

        Args:
            ts: The time series to write.
            start: The starting date from which data will be written.
            end: The ending date until which data will be written.
            auto_create: Create the time series if not exists in the back end.

        Examples:
            .. code-block:: python

                ts = store1.get_by_id(47122)
                store2.write_time_series(ts)

        """
        pass

    def create_time_series_from(self, copy_from: TimeSeries) -> TimeSeries:
        """
        Create a time series as a copy from another existing time series e.g. from another system.
        This function only copies meta data and only if the underlaying backend supports it.

        Args:
            copy_from: The time series object to be copied.
        """
        return self.create_time_series(copy_from.path, copy_from.name, copy_from.metadata)

    @abstractmethod
    def create_time_series(self, path: str, display_name: str, attributes: Mapping=None,
                           params: Mapping[str, Any]=None) -> TimeSeries:
        """Create an empty time series.

        Args:
            path: The time series path.
            display_name: The time series name to display.
            attributes: The metadata of the time series.
            params: The additional parameters, which are passed to the backend.
        """
        pass

    def __getitem__(self, item: Union[int, str]) -> TimeSeries:
        if isinstance(item, int):
            return self.get_by_id(item)
        else:
            return self.get_by_path(item)
