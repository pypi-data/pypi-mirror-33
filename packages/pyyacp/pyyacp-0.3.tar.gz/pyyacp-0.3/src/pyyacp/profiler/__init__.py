#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import structlog

from pyyacp.profiler.empty_cell_detection import is_not_empty

log = structlog.get_logger()


class ColumnProfilerSet(object):
    """
    This class provides a wrapper for profilers which take a column as input
    """
    def __init__(self, profilers=[]):
        self.profiler_factories=profilers

    def _init(self):
        self.profilers=[p() for p in self.profiler_factories]

    def profile_column(self, column, meta):
        self._init()
        for p in self.profilers:
            result = p.profile_column(column, meta)
            self._add_results(meta, result, p)

    def _add_results(self, meta, results, p):
        if isinstance(results, dict):
            for k, v in results.items():
                meta["{}_{}".format(p.key, k)] = v
        else:
            meta["{}".format(p.key)] = results


class ColumnByCellProfilerSet(ColumnProfilerSet):

    def __init__(self, profilers=[]):
        super(ColumnByCellProfilerSet, self).__init__(profilers=profilers)

    def profile_column_by_cell(self, column, meta):
        self._init()
        pa=[p.accept for p in self.profilers]

        for cell in column:
            for p in pa:
                p(cell)
        for p in self.profilers:
            result = p.result()
            self._add_results(meta, result, p)

    def profile_column(self, column, meta):
        self.profile_column_by_cell(column, meta)



class Profiler(object):
    def __init__(self, id, key):
        self.id=id
        self.key=key

class TableProfiler(Profiler):
    def __init__(self, id, key):
        super(TableProfiler, self).__init__(id,key)

    def profile_table(self, table):
        pass

class ColumnProfiler(Profiler):
    def __init__(self, id, key):
        super(ColumnProfiler, self).__init__(id,key)

    def profile_column(self, column, meta):
        pass

class ColumnByCellProfiler(Profiler):
    def __init__(self, id, key):
        super(ColumnByCellProfiler, self).__init__(id,key)

    def result(self):
        pass

    def accept(self, cell):
        pass


class ColumnRegexProfiler(Profiler):
    def __init__(self):
        super(ColumnRegexProfiler, self).__init__('crp','col_regex')
        self.values=[]

    def profile_column(self, column, meta):
        return dtpattern.aggregate(column, size=self.num_patterns)

    def result(self):
        res=self.profile_column(self.values, None)
        self.values=[]
        return res

    def accept(self, cell):
        self.values.append(cell)

    def _profile(self, table):
        for i, col in enumerate(table.columns()):
            try:
                regex = regroup.DAWG.from_iter(col).serialize()
                table.column_metadata[i][self.key]=regex
            except Exception as e:
                table.column_metadata[i][self.key]="exc:{}".format(str(e.__class__))





