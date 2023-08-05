#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import traceback

import sys

import  pyyacp.datatable as datatable

from pyyacp.table_structure_helper import AdvanceStructureDetector


#filename=csv_file
from pyyacp import YACParser

from pyyacp.profiler.profiling import apply_profilers

url='http://nsandi-corporate.com/wp-content/uploads/2015/02/transparency-25k-08-2013.csv'
url='http://www.win2day.at/download/lo_1992.csv'
url='http://data.wu.ac.at/data/unibib/diff/JREK/2015-07-07.csv'
url='http://www.win2day.at/download/etw_2006.csv'
url='http://www.win2day.at/download/jo_2004.csv'
url='http://www.win2day.at/download/jo_1992.csv'
url='http://www.wien.gv.at/politik/wahlen/ogd/bv151_99999999_9999_spr.csv'


url='http://www.win2day.at/download/tw_2002.csv'
url='http://wko.at/statistik/opendata/sm/OGD_mgstat_sm_s11-1_bld_sp4.csv'
url='http://wahlen.tirol.gv.at/gemeinderatswahl_2010/dokumente/wahl25.csv'
url='http://www.win2day.at/download/etw_2001.csv'
url='http://www.wien.gv.at/statistik/ogd/vie_106.csv'
#url='http://data.wu.ac.at/portal/dataset/fdb16224-5f6c-482b-932f-e5fe12f52991/resource/a545bb37-0563-4312-be3f-b36a793c0764/download/allcoursesandorgid14s.csv'




structure_detector = AdvanceStructureDetector()





def profile(url, filename,max_tables=1, sample_size=1800):
    yacp = YACParser(filename=filename, url=url, structure_detector=structure_detector, sample_size=sample_size)
    if url is None:
        url='http://example.org/table'
    tables = datatable.parseDataTables(yacp, url=url, max_tables=max_tables)

    if max_tables==1:
        table=tables


    apply_profilers(table)


    table.print_summary()


url=None
url="http://data.statistik.gv.at/data/OGD_bpihbaugg2015_BPI_H2015_1_C-A10-0.csv"
filename=None
#filename="/Users/jumbrich/data/csv_catalog_new/data/8/1906eab434e57878a013fbd4622257cc775375a8/856294b5a0f32a4d941843c7dadac1ad.gz"
profile(url=url,filename=filename)
