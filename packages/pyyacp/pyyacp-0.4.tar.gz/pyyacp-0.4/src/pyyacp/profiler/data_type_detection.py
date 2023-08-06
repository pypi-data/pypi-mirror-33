
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from pyyacp.profiler import ColumnProfiler

from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from pyjuhelpers.timer import timer

INT='int'
FLOAT='float'
DATETIME='datetime'
DATE='date'
TIME='time'
UNICODE='unicode'

import re
types=[
    (FLOAT,re.compile('^\[?[+/-]*\]?\d+\.\d*$')),
    (INT,re.compile('^\[?[+/-]*\]?\d+$')),
    (DATETIME, re.compile('^\d{4}-\d{2}-\d{2}([C ]+\d{2}:\d{2}:\d{2})$')),
    (DATE, re.compile('^\d{4}-\d{2}-\d{2}$')), #1111-11-11
    (DATE, re.compile('^\d{4}/\d{2}/\d{2}$')), #1111/11/11
    (DATE, re.compile('^\d{2}/\d{2}/\d{4}$')),#11/11/1111

    (TIME, re.compile('^\d{2}:\d{2}(:\d{2})?$')) #1111-11-11
]

class DataTypeDetection(ColumnProfiler):

    def __init__(self):
        super(DataTypeDetection, self).__init__('dtype','data_type')

    def result_datatype(self):
        return str

    @timer(key="profile.col_dtype")
    def _profile_column(self, values, meta):

        data_type = UNICODE
        if 'pattern' not in meta:
            ColumnPatternProfiler().profile_column(values, meta)
        pattern = meta['pattern']

        gtypes = set([])
        for ptype in types:
            if pattern is not None:
                m = ptype[1].match(pattern)
                if m:
                    gtypes.add(ptype[0])
        if len(gtypes) != 1:
            data_type =  UNICODE
        if len(gtypes)==1:
            data_type = gtypes.pop()
            if data_type == INT or data_type == FLOAT:
                if 'stats_min_value' in meta:
                    smallest_first_char = meta['stats_min_value'][0]
                    if smallest_first_char == u'0':
                        # print "LEADING ZERO"
                        return UNICODE

        return data_type


