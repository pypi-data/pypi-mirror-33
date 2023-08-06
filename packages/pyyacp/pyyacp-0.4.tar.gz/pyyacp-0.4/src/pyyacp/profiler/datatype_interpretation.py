#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from pyyacp.profiler import ColumnProfiler
from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler

import re

from pyyacp.profiler.data_type_detection import DataTypeDetection

SENT=re.compile('^(C[c])+( [Cc]+)*[\.!?]?$')
ENT=re.compile('^(C[c])+( [Cc]+){2,3}$')

from pyjuhelpers.timer import timer

class DataTypeInterpretation(ColumnProfiler):

    def __init__(self):
        super(DataTypeInterpretation, self).__init__('dclass','data_class')

    def result_datatype(self):
        return str

    @timer(key="profile.col_dclass")
    def _profile_column(self, column, meta):
        if 'pattern' not in meta:
            ColumnPatternProfiler().profile_column(column, meta)
        if 'stats_max_len' not in meta:
            ColumnStatsProfiler().profile_column(column, meta)
        if 'data_type' not in meta:
            DataTypeDetection().profile_column(column, meta)

        return self._analyse_ColumnPattern(column,meta)

    def _analyse_ColumnPattern(self, column,meta):
        from pyyacp.profiler.data_type_detection import DATETIME, INT, UNICODE
        patterns = meta['pattern']
        data_type=meta['data_type']
        #print meta
        min, mean, max = meta['stats_max_len'], meta['stats_mean_len'], meta['stats_min_len']
        fixed_len = min ==max
        unique = meta['stats_distinct'] + meta['stats_empty'] == meta['stats_num_rows']

        if data_type==DATETIME:
            return data_type.upper()

        if meta['stats_empty'] == meta['stats_num_rows']:
            return "EMPTY"

        s=''
        if data_type == INT:
            s+='NUM'
        elif data_type == UNICODE:
            if patterns:
                if SENT.match(patterns):
                    s+='SENTENCE'
                elif ENT.match(patterns):
                    s += 'ENTITY'
                else:
                    s += 'UNI'
            else:
                s += 'UNI'
        else:
            s = 'UNDEF'

        if fixed_len:
            s+='_ID'
        else:
            s+='_VAR'

        if unique:
            s+='_UNIQ'

        if meta['stats_distinct'] == 1:
            s+="_SING"
        elif (meta['stats_num_rows'] > 10 and (meta['stats_distinct']/float(meta['stats_num_rows']))<0.1) \
                or (meta['stats_num_rows'] < 10 and meta['stats_distinct']<=2):
            s+='_CAT'
        return s
