#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

from pyyacp.html.to_html import to_html
import  pyyacp.datatable as datatable
from pyyacp.profiler import ColumnByCellProfilerSet, \
    ColumnProfilerSet
from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from profiler.profiling import apply_profilers

from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.datatype_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler, BenfordsLawDistribution
from pyyacp.table_structure_helper import AdvanceStructureDetector
from pyyacp.testing.csv_iterator import csvContent_iter

SAMPLES_PATH = "./sample_csvs"
from os import listdir
from os.path import isfile, join
onlyfiles = [join(SAMPLES_PATH, f) for f in listdir(SAMPLES_PATH) if isfile(join(SAMPLES_PATH, f))]




def from_csv_iter(portalID='data_wu_ac_at', snapshot=None):
    profilers=[ColumnPatternProfiler(),DataTypeDetection(), ColumnStatsProfiler()]#FDProfiler(), ,ColumnStatsProfiler(), DataTypeDetection()]#,XSDTypeDetection()] #,ColumnRegexProfiler()]#,XSDTypeDetection()],,ColumnStatsProfiler()
    cnt=0
    for uri, csv_file in csvContent_iter(portalID, snapshot=snapshot):
        cnt+=1
        print("{}, {} -> {}".format(cnt,uri, csv_file))
        try:

            from pyyacp.pyyacp import YACParser
            yacp = YACParser(filename=csv_file,sample_size=1800, structure_detector = AdvanceStructureDetector())
            table=datatable.parseDataTables(yacp, url=uri)
            profilers=[ColumnByCellProfilerSet([ColumnPatternProfiler, ColumnStatsProfiler, CharacterDistributionProfiler, BenfordsLawDistribution]) , ColumnProfilerSet([DataTypeDetection,DataTypeInterpretation])]
            apply_profilers(table,profilers=profilers)



            to_html(table, cnt, dir='.')

        except Exception as e:
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print(e)
        #print'next'
        if cnt>10:
            break

if __name__ == '__main__':
    from_csv_iter(snapshot=1803)
