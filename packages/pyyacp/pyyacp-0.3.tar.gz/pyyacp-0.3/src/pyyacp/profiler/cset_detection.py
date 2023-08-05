#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from dtpattern.dtpattern1 import translate_all, l1_aggregate, l2_aggregate, patterns_to_unique_symbols
from pyyacp.profiler import ColumnProfiler
from pyyacp.profiler.data_type_detection import DATETIME, INT, UNICODE

import re
SENT=re.compile('^(C[c])+( [Cc]+)*[\.!?]?$')
ENT=re.compile('^(C[c])+( [Cc]+){2,3}$')

class CSetDetection(ColumnProfiler):

    def __init__(self):
        super(CSetDetection, self).__init__('cset','cset')


    def profile_column(self, column, meta):

        return self._analyse_ColumnPattern(column, meta)


    def _analyse_ColumnPattern(self, column,meta):
        patterns = translate_all(column)

        res=set([])
        for p in patterns:
            s=set(p)
            res.update(s)



        return ''.join(sorted(list(set(res))))


