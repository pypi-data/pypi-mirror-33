#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import operator
from collections import defaultdict

import numpy as np

from pyyacp.profiler import ColumnProfiler
from pyjuhelpers.timer import timer

__author__ = 'nina'

ColumnStatsProfilerResult = collections.namedtuple('ColumnStatsProfilerResult',
                                                  ['num_rows',
                                                   'min_value','max_value',
                                                    'min_len','max_len','mean_len','median_len',
                                                   'empty','distinct','uniqueness','mode','constancy'
                                                   ])
ColumnStatsProfilerResult.__new__.__defaults__ = (0,) * len(ColumnStatsProfilerResult._fields)
class ColumnStatsProfiler(ColumnProfiler):

    def __init__(self):
        super(ColumnStatsProfiler, self).__init__('csp', 'stats')
        self.vlen = []
        self.dv = defaultdict(int)

    @timer(key="profile.col_stats")
    def _profile_column(self, values, meta)->ColumnStatsProfilerResult:
        """

        :param values:
        :param meta:
        :return: instance of ColumnStatsProfilerResult
        """
        _vlena= self.vlen.append
        for v in values:
            _v = v.strip()
            _vlena(len(_v))
            self.dv[_v]+=1
        return self._compile_stats()

    def result_datatype(self):
        return ColumnStatsProfilerResult()

    def _compile_stats(self):
        stats={}
        stats['num_rows'] = len(self.vlen)

        a = np.array(self.vlen)
        an = a[a>0]

        if len(a[a==0])>0:
            if '' in self.dv:
                self.dv.pop('')

        stats['min_value'] = min(self.dv) if len(self.dv)>0 else ''
        stats['max_value'] = max(self.dv) if len(self.dv)>0 else ''


        stats['min_len'] = min(an) if len(an)>0 else 0
        stats['max_len'] = max(an) if len(an)>0 else 0
        stats['mean_len'] = np.mean(an)
        stats['median_len'] = np.median(an)

        stats['empty']= len(a[a==0])
        stats['distinct']=len(self.dv)
        stats['uniqueness']=len(self.dv)/float(len(a)) if len(a)>0 else 0

        sorted_values = sorted(self.dv.items(), key=operator.itemgetter(1), reverse=True)
        top_values = [(sorted_values[i][0], int(sorted_values[i][1])) for i in range(min(5, len(self.dv)))]

        stats['mode'] = sorted_values[0][0] if len(sorted_values)>0 else None

        stats['constancy'] = max(self.dv.values()) / float(len(a)) if len(self.dv)>0 and  len(a)>0 else 0

        return ColumnStatsProfilerResult(**stats)
