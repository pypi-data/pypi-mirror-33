#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import hashlib
import inspect
import itertools
import logging
from io import StringIO

import anycsv
import pandas as pd
import csv

from pyjuhelpers.logging import log_func_detail
from pyjuhelpers.module_import import import_from_string
from pyyacp.config import pyyacpconfig, anycsvconfig

from pyyacp.table_structure_helper import _most_common_oneliner


from pyyacp import YACParserException

from pyjuhelpers.string_format import reindent

import structlog
log = structlog.get_logger()



def grouper(iterable, size):
    """
        batch_group generator
    :param n:
    :param iterable:
    :return:
    """
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


@log_func_detail(log, level=logging.INFO, log_time=True)
def parseDataTables(csv,
                    skip_guess_encoding = anycsvconfig.SKIP_GUESS_ENCODING,
                    sniff_lines = anycsvconfig.NO_SNIFF_LINES,
                    max_file_size = anycsvconfig.MAX_FILE_SIZE,
                    encoding = anycsvconfig.DEFAULT_ENCODING,
                    batch_size = pyyacpconfig.BATCH_SIZE, structure_detector = pyyacpconfig.DEFAULT_STRUCTURE_DETECTOR,
                    max_tables=pyyacpconfig.MAX_TABLES, raiseError=pyyacpconfig.RAISE_ERROR):
    """

    :param csvreader:
    :param batch_size:
    :param structure_detector:
    :param max_tables:
    :param raiseError: in case we parse more than max_tables , we raise an error if flag is True
    :return:
    """

    csvreader = anycsv.reader(csv,
                           skip_guess_encoding = skip_guess_encoding,
                           sniff_lines = sniff_lines, max_file_size = max_file_size, encoding = encoding)


    if isinstance(structure_detector, str):
        structure_detector = import_from_string(structure_detector)
    if inspect.isclass(structure_detector):
        structure_detector= structure_detector()

    if isinstance(csvreader, anycsv.csv_parser.Table):
        csv=csvreader.csv
        encoding = csvreader.encoding
        dialect = csvreader.dialect
    else:
        csv = None
        encoding = None
        dialect = None


    tables = []

    cur_dt = None


    skipped = 0

    rows_to_add=[]

    row_len_groups = [] # list of row_len_groups
    rows_parsed = 0 # count to keep track how many rows we parsed already



    for g_rows in grouper(csvreader, batch_size):
        rows_parsed += len(g_rows)

        # analys the shape of the rows
        _row_lens = list(map(len, g_rows))
        _row_len_groups = [(k, sum(1 for i in g)) for k, g in itertools.groupby(_row_lens)]
        _max_len = max(_row_lens)
        _est_colNo = _most_common_oneliner(_row_lens)

        row_len_groups += _row_len_groups

        if len(_row_len_groups) == 1:
            # perfect, one table in this batch, all rows have the same length
            if cur_dt is None:
                # we have no table, this is hte first
                g_rows = list(g_rows)

                #detect comment and header based on the rows in the current batch
                comments = structure_detector.guess_description_lines( g_rows )
                header = structure_detector.guess_headers(g_rows)

                cur_dt = DataTable( csv, encoding, dialect, _est_colNo, comments=comments, headers=header)

                pos = len(comments) + len(header) #get position of data rows
                rows_to_add.extend( g_rows[pos:] ) # one group, add remaining rows as data rows

            elif _max_len == cur_dt.no_cols:
                #ok we have an active table and the current batch has the same cols as our table -> assume that they belong together
                rows_to_add.extend(g_rows)
            else:

                # not the same length, maybe different table , should not happen
                #create a new table
                # g_rows = list(g_rows)
                #
                # # detect comment and header based on the rows in the current batch
                # comments = structure_detector.guess_description_lines(g_rows)
                # header = structure_detector.guess_headers(g_rows)
                #
                # cur_dt = DataTable(csv, encoding, dialect, _est_colNo, comments=comments, headers=header)
                #
                # pos = len(comments) + len(header)  # get position of data rows
                # rows_to_add.extend(g_rows[pos:])  # one group, add remaining rows as data rows

                log.warning("NOT IMPLEMENTED", csv=csv,
                            msg="not the same length, maybe different table")
        else:
            # lets go over the groups
            # (2,30) -> belongs to old table
            # (0,1)  -> empty line
            # (1,1)  -> comment line -> flag create_new
            # (4,20) -> belongs to new table -> create new table, start parsing at (1,1)

            cur_line = 0
            create_new = False
            for i, group in enumerate(_row_len_groups):

                _cols = group[0]
                _no_rows = group[1]



                if _cols == 0:   # empty line, skip, 0 columns
                    skipped += 1
                    pass
                elif _cols == 1 and _no_rows < 3:
                    # there is a group with one element, that should be the comment lines
                    # also this means a new table
                    if i == len(_row_len_groups) - 1 and [sum(x) for x in zip(*_row_len_groups)][1] < batch_size:
                        #no idea what i do here
                        # print "SUFFIX COMMENT LINES"
                        log.warning("SUFFIX COMMENT LINES")
                    else:
                        # we have more groups to come, so lets start a new table from this line
                        if not create_new:
                            parse_start = cur_line
                        create_new = True
                else:
                    # a group with more than one column
                    start = None
                    if cur_dt is None or create_new:
                        start = cur_line
                        if create_new:
                            start = parse_start
                    elif _cols == cur_dt.no_cols:
                        #cur_dt.addRows(g_rows[cur_line:group[1]])
                        rows_to_add.extend(g_rows[cur_line:cur_line+group[1]])
                    else:
                        # seems like a new table
                        if _no_rows != 1 or (
                                        i == len(_row_len_groups) - 1 and
                                        [sum(x) for x in zip(*_row_len_groups)][1] == batch_size):
                            # more than one row
                            # OR at the end of the group and still a full batch
                            start = cur_line
                        else:
                            #print ("NOT TREATED", group[0])
                            # if only one row and (at the end of the file or in the middle of a group)
                            pass

                    if start is not None:
                        if cur_dt:
                            cur_dt.addRows(rows_to_add)
                            rows_to_add=[]

                            cur_dt.done()
                            tables.append(cur_dt)

                        _rows=g_rows[start:cur_line+_no_rows]
                        comments = structure_detector.guess_description_lines(_rows)
                        header = structure_detector.guess_headers(_rows)

                        cur_dt = DataTable( csv, encoding, dialect, _cols, comments=comments, headers=header)

                        pos = len(comments) + len(header) + start
                        end = cur_line + _no_rows

                        rows_to_add.extend(g_rows[pos:end])
                        create_new = False

                cur_line += _no_rows

    cur_dt.addRows(rows_to_add)
    rows_to_add = []
    cur_dt.done()
    tables.append(cur_dt)

    prev_group = None
    agg_groups = []
    for group in row_len_groups:
        if prev_group is not None:
            if prev_group[0] == group[0]:
                # merge
                prev_group = ( prev_group[0], prev_group[1] + group[1])
            else:
                agg_groups.append(prev_group)
                prev_group = group
        else:
            prev_group = group

    agg_groups.append(prev_group)
    log.info("TABLE SHAPE", groups=agg_groups, csv=csv)

    if len(tables) > max_tables:
        if raiseError:
            raise YACParserException("Too many tables (#{}) shapes:{}, csv:{}".format(len(tables),str(agg_groups), csv))
    log.info("Parsed table", skipped=skipped, tables=len(tables), csv=csv)

    if max_tables == 1:
        return tables[0]
    else:
        return tables


def create_column_names(header_rows, cols=None):
    if cols is None:
        cols = len(header_rows)
    names=[]
    done=False
    if len(header_rows) >= 1:
        #we found at least one header row

        #lets check if there is any header row with values in each column
        for h_row in header_rows:
            if all( h is not None and len(h.strip())>0 for h in h_row):
                #all header have a non empty value
                names = [h.strip() for h in h_row]
                done = True
                break
        if not done:
            #ok second attemp, take always the first available header
            h_transposed = list(map(list, zip(*header_rows)))
            for i, hs in enumerate(h_transposed):
                try:
                    name=next(s for s in hs if s and len(s.strip())>0)
                except:
                    name="miss{}".format(i+1)
                names.append(name)
    else:
        names = ['col{}'.format(i) for i in range(1, cols+1)]

    ##check that we do not have duplicates
    newlist = []
    for i, v in enumerate(names):
        totalcount = names.count(v)
        count = names[:i].count(v)
        newlist.append(v + str(count + 1) if totalcount > 1 else v)
    names = newlist

    return names


DataTableMetaData = collections.namedtuple('DataTableMetaData',
                                           ['csv', 'encoding', 'dialect', 'digest',
                                            'comment_rows','header_rows',
                                            'no_cols','no_rows','column_names'])


class DataTable(object):

    def __init__(self, csv, encoding, dialect, cols, comments=None, headers=None):
        self.csv=csv
        self.encoding=encoding
        self.dialect = dialect

        self.hash = hashlib.md5()
        self.digest =None

        self.comment_rows = comments if comments else []
        self.header_rows = headers if headers else []

        for c in self.comment_rows:
            self.hash.update("".join(c).encode('utf-8'))
        for c in self.header_rows:
            self.hash.update( "".join(c).encode('utf-8'))

        #store the dimensionality of the table
        self.no_cols = cols
        self.no_rows = 0

        self.column_names = create_column_names(self.header_rows,self.no_cols)

        self.data=pd.DataFrame(columns=self.column_names)

    def shape(self):
        """
        :return: tuple (rows, columns
        """
        return (self.no_rows, self.no_cols)

    @property
    def metadata(self) ->  DataTableMetaData:
        return DataTableMetaData(self.csv,
                                 self.encoding,
                                 self.dialect,
                                 self.digest,
                                 self.comment_rows,
                                 self.header_rows,
                                 self.no_cols,
                                 self.no_rows,
                                 self.column_names)

    def addRows(self, rows):
        try:
            for c in rows:
                self.hash.update("".join(c).encode('utf-8'))

            df = pd.DataFrame( list(rows), columns=self.column_names)
            self.data=pd.concat([self.data,df])
            self.no_rows = self.data.shape[0]
        except Exception as e:
            log.fatal("Exception In Adding Rows", exc_info=e)

    def rows(self):
        return [row for row in self.rowIter()]

    def rowIter(self):
        for row in self.data.itertuples():
            yield list(row[1:])


    def columnIter(self):
        for colName in self.column_names:
            yield self.data[colName].tolist()

    def columns(self):
        return [collist for collist in self.columnIter()]


    def done(self):
        self.digest = self.hash.hexdigest()
        self.hash=None
        del self.hash

    def generate(self, delimiter=',', newline='\n', header=True, comments=True):
        """
        :param delimiter: The delimiter symbol. The default is ",".
        :param newline: The line separator. The default is "\n".
        :param header: There will be a header in the output (if no header detected then col0,col1, ...)
        :param commentPrefix: The prefix for comments in the first rows. If false, any comments will be ignored.
        :return: A string representation of the CSV table
        """
        csvstream = StringIO()
        w = csv.writer(csvstream,  delimiter=str(delimiter), lineterminator=str(newline))
        c=0
        # write description lines at top
        if comments:
            for line in self.comments:
                w.writerow(line)
                c+=1
        if header:
            for header in self.header_rows:
                w.writerow([str(h) for h in header])
                c += 1
        for row in self.rowIter():
            w.writerow([str(r) for r in row])
            c += 1
        return csvstream.getvalue()


    def print_summary(self):

        print("{:#^80}".format(' TABLE STRUCTURE '))
        for k, v in self.metadata._asdict().items():
            print("#  {:>15}: {}".format(k,v))








