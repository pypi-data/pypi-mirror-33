#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import inspect

import structlog
log = structlog.get_logger()

from pyyacp.profiler.empty_cell_detection import is_not_empty


def isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple: return False
    f = getattr(t, '_fields', None)
    if not isinstance(f, tuple): return False
    return all(type(n)==str for n in f)


from abc import abstractmethod
class Profiler(object):
    def __init__(self, id, key):
        self.id=id
        self.key=key


    @abstractmethod
    def result_datatype(self):
        """

        :return: the datatype of the profiler result object
        """
        pass

    def _add_results(self, meta, results):

        if isnamedtupleinstance(results):
            for k, v in results._asdict().items():
                meta["{}_{}".format(self.key, k)] = v
        elif isinstance(results, dict):
            for k, v in results.items():
                meta["{}_{}".format(self.key, k)] = v
        else:
            meta["{}".format(self.key)] = results



    def profiler_keys(self):
        results = self.result_datatype()

        keys=[]
        if isnamedtupleinstance(results):
            for k, v in results._asdict().items():
                keys.append("{}_{}".format(self.key, k))
        elif isinstance(results, dict):
            for k, v in results.items():
                keys.append("{}_{}".format(self.key, k))
        else:
            keys.append("{}".format(self.key))

        return keys

    def isProfiled(self, meta):
        for k in self.profiler_keys():
            if k not in meta:
                return False
        return True



class TableProfiler(Profiler):
    def __init__(self, id, key):
        super(TableProfiler, self).__init__( id, key)


    def profile_table(self, table):
        if not self.isProfiled(table.table_metadata):
            result = self._profile_table(table)
            self._add_results(table.table_metadata, result)


    @abstractmethod
    def _profile_table(self, table):
        """

        :param table:
        :return: the profiler result object
        """
        pass


class ColumnProfiler(Profiler):
    def __init__(self, id, key):
        super(ColumnProfiler, self).__init__(id,key)

    def profile_column(self, column, meta):
        if not self.isProfiled(meta):
            result = self._profile_column(column, meta)
            self._add_results(meta, result)



    @abstractmethod
    def _profile_column(self, column, meta):
        """

        :param column: the column data
        :param meta: the current column metadata
        :return: the profile object
        """
        pass

class ColumnProfilerSet(object):
    """
    This class provides a wrapper for profilers which take a column as input
    """
    def __init__(self, profilers=[]):
        self.profilers=profilers


    def profile_column(self, column, meta):
        for p in self.profilers:
            if inspect.isclass(p):
                p=p()
            p.profile_column(column, meta)


class TableProfilerSet(object):
    def __init__(self, profilers=[]):
        self.profiler_factories=profilers


    def profile_table(self, table):
        for p in self.profilers:
            if inspect.isclass(p):
                p=p()
            p.profile_table(table)



