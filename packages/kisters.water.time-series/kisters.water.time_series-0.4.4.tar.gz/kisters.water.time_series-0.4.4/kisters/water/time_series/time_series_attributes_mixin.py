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

from abc import abstractmethod
from typing import Any, Mapping, MutableMapping, Union

from kisters.water.time_series.time_series import TimeSeries


class TimeSeriesAttributesMixin(TimeSeries):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(TimeSeriesAttributesMixin, self).__init__()

    def __str__(self) -> str:
        return "{}({})".format(self.path, str(self.id))

    def __repr__(self, *args, **kwargs) -> str:
        return "{}({})".format(self.path, str(self.id))

    @abstractmethod
    def _raw_metadata(self) -> MutableMapping[str, Any]:
        pass

    def _safe_meta(self, key: str) -> Union[int, str, None]:
        m = self._raw_metadata()
        if key not in m:
            return None
        return m[key]

    @property
    def name(self) -> str:
        return self._safe_meta('name')

    @property
    def id(self) -> int:
        return self._safe_meta('id')

    @property
    def short_name(self) -> str:
        return self._safe_meta('shortName')

    @property
    def path(self) -> str:
        return self._safe_meta('tsPath')

    @property
    def metadata(self) -> MutableMapping[str, Any]:
        m = self._raw_metadata().copy()
        m["tsPath"] = self.path
        m["id"] = self.id
        m["name"] = self.name
        m["shortName"] = self.short_name
        m["dataCoverageFrom"] = self.coverage_from
        m["dataCoverageUntil"] = self.coverage_until
        return m
