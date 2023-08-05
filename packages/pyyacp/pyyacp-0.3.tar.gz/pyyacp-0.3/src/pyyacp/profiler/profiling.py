#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from pyyacp.timer import timer, Timer

from pyyacp.profiler import  ColumnProfilerSet, ColumnByCellProfilerSet
from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.data_type_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler, BenfordsLawDistribution
from pyyacp.profiler.fdprofiler import FDProfiler



default_profilers = [ColumnByCellProfilerSet(
        [ColumnPatternProfiler, ColumnStatsProfiler, CharacterDistributionProfiler, BenfordsLawDistribution]),
                 ColumnProfilerSet([DataTypeDetection, DataTypeInterpretation])]

@timer(key="profile_table", verbose=False)
def apply_profilers(table, profilers=default_profilers):
    for i, col in enumerate(table.columns()):
        with Timer(key='column_profilers', verbose=False):
            for profiler in profilers:
                if isinstance(profiler, ColumnProfilerSet):
                    profiler.profile_column(col, table.column_metadata[i])

    with Timer(key='table_profilers', verbose=False):
        for profiler in profilers:
            if not isinstance(profiler, ColumnProfilerSet):
                profiler().profile_table(table)

