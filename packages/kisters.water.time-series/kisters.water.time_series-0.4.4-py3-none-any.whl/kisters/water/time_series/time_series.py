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
from typing import Any, Mapping, MutableMapping

from pandas.core.frame import DataFrame


class TimeSeries(ABC):
    """This is class provides the interface of TimeSeries."""

    def __init__(self):
        pass

    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def coverage_from(self) -> datetime:
        """
        The date from which the TimeSeries data starts.

        Returns:
            The start date
        """
        pass

    @property
    @abstractmethod
    def coverage_until(self) -> datetime:
        """
        The date until which the TimeSeries data covers.

        Returns:
            The end date
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The full name of the TimeSeries.

        Returns:
            The full name
        """
        pass

    @property
    @abstractmethod
    def id(self) -> int:
        """
        The id number which fully identifies the TimeSeries.

        Returns:
            The id number
        """
        pass

    @property
    @abstractmethod
    def short_name(self) -> str:
        """
        The short name of the TimeSeries.

        Returns:
            The short name
        """
        pass

    @property
    @abstractmethod
    def path(self) -> str:
        """
        The full path to this TimeSeries.

        Returns:
             The path string
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> MutableMapping[str, Any]:
        """
        The map containing all the metadata related to this TimeSeries.

        Returns:
             The metadata map
        """
        pass

    @abstractmethod
    def read_data_frame(self, start: datetime=None, end: datetime=None, params: Mapping=None) -> DataFrame:
        """
        This method returns the TimeSeries data between the start and end dates (dates data included)
        structured as a pandas DataFrame.

        Args:
            start: The starting date from which the data will be returned.
            end: The ending date until which the data will be covered (end date included).
            params: The parameters passed to the backend call.

        Returns:
            The DataFrame containing the TimeSeries data
        """
        pass

    @abstractmethod
    def write_data_frame(self, data_frame: DataFrame):
        """
        This methods writes the TimeSeries data inside data_frame into this TimeSeries.

        Args:
            data_frame: The TimeSeries data to be written in the form of a pandas DataFrame.
        """
        pass
