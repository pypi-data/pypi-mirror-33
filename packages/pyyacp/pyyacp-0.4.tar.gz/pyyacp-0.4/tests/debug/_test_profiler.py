#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

import  pyyacp.datatable as datatable
from pyyacp import YACParser
from pyyacp.table_structure_helper import AdvanceStructureDetector

from pyyacp.profiler.fdprofiler import FDProfiler
from pyyacp.profiler import ColumnProfilerSet, ColumnByCellProfilerSet
from pyyacp.profiler.profiling import apply_profilers
from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.cset_detection import CharacterSetProfiler
from pyyacp.profiler.datatype_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler, BenfordsLawDistribution
from pyyacp.table_structure_helper import AdvanceStructureDetector












structure_detector=AdvanceStructureDetector


default_profilers = [FDProfiler, ColumnByCellProfilerSet(
            [ColumnPatternProfiler, ColumnStatsProfiler, CharacterDistributionProfiler, BenfordsLawDistribution]),
                     ColumnProfilerSet([DataTypeDetection, DataTypeInterpretation, CharacterSetProfiler])]






def profile_csv(csv_file):
    try:



        # filename=csv_file

        yacp = YACParser(filename=csv_file, sample_size=1800, structure_detector=AdvanceStructureDetector())
        table = datatable.parseDataTables(yacp, url="http://example.org/")

        apply_profilers(table, profilers=default_profilers)


    except Exception as e:
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print(e)


csv_file="/Users/jumbrich/data/mimesis_csvs/dummy/de-at_address_r100xc20.csv"
profile_csv(csv_file)
