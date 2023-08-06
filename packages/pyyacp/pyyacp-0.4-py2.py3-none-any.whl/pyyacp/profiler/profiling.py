import collections
import inspect

from pyjuhelpers.module_import import import_from_string
from pyjuhelpers.string_format import reindent
from pyyacp.config import pyyacpconfig
from pyyacp.datatable import DataTable
from pyyacp.profiler import Profiler, ColumnProfilerSet, ColumnProfiler, TableProfilerSet, TableProfiler

from pyjuhelpers.timer import timer
import pandas as pd

TableProfile = collections.namedtuple('TableProfile',['table_metadata','table_profile', 'col_profiles'])
class ProfiledDataTable(DataTable):

    def __init__(self, datatable):
        if datatable is not None:
            self.__dict__.update(datatable.__dict__)

        self.table_metadata = {}
        self.column_metadata = {i: {} for i in range(0, len(datatable.column_names))}
        self._profiler_keys={}

    def update_profiler_keys(self, key_dict):
        for k, v in key_dict.items():
            if k in self._profiler_keys:
                self._profiler_keys[k] += v
            else:
                self._profiler_keys[k] = v

    @property
    def profiler_keys(self):
        return self._profiler_keys

    @property
    def table_profiler_keys(self):
        return self._profiler_keys['table']

    def colum_profiles_df(self)-> pd.DataFrame:
        """

        :return: a pandas data frame
        """
        d={}
        for i in range(0, self.no_cols):
            dd=d.setdefault('col{}'.format(i+1),{})
            for a,h in enumerate(self.header_rows):
                dd['header{}'.format(a)]=h[i]
            for k,v in self.column_metadata[i].items():
                dd[k]=v

        return pd.DataFrame(d)

    @property
    def column_profiler_keys(self):
        return self._profiler_keys['column']

    def col_profile_dict(self):
        col_profiles={}
        for col, meta in self.colum_profiles_df().to_dict().items():
            col_profiles[col] = {k: meta[k] for k in self.column_profiler_keys if k in meta}
            col_profiles[col]['col'] = col
        return col_profiles

    def table_profile(self):
        return self.table_metadata

    def print_summary(self):
        super(ProfiledDataTable, self).print_summary()

        print ("#  {:=^76}".format(' TABLE META '))
        for k,v in self.table_profile().items():
            print("#  {:>15}: {}".format(k, v))

        print("#  {:=^76}".format(' COLUMN PROFILE '))

        print (reindent(self.colum_profiles_df().to_string(line_width=80), 5,prefix="#"))

        print("#  {:-^76}".format(" DATA {} ".format(self.data.shape)))

        print(reindent(self.data.head(5).to_string(index=False,line_width=80),5, prefix="#"))

    def profiledata(self):
        return TableProfile(self.metadata, self.table_profile(), self.col_profile_dict())



@timer()
def apply_profilers(table, profilers = pyyacpconfig.DEFAULT_PROFILERS ) -> ProfiledDataTable:

    if not isinstance(table, ProfiledDataTable) and isinstance(table, DataTable):
        table = ProfiledDataTable(table)

    if isinstance(profilers, list):
        for p in profilers:
            if isinstance(p, str):
                p = import_from_string(p)
            apply_profiler(table,p)

    elif isinstance(profilers, Profiler) or issubclass(profilers, Profiler):
        apply_profiler(table, profilers)

    return table

def apply_profiler(table, profiler) -> ProfiledDataTable:
    if not isinstance(table, ProfiledDataTable) and isinstance(table, DataTable):
        table = ProfiledDataTable(table)

    if inspect.isclass(profiler):
        profiler = profiler()

    table.update_profiler_keys(get_profiler_keys(profiler))

    if isinstance(profiler, ColumnProfilerSet) or isinstance(profiler, ColumnProfiler):
        for i, col in enumerate(table.columns()):
            profiler.profile_column(col, table.column_metadata[i])
    elif isinstance(profiler, TableProfilerSet) or isinstance(profiler, TableProfiler):
        profiler.profile_table(table)

    return table

def get_profilers_keys(profilers = pyyacpconfig.DEFAULT_PROFILERS ):
    keys = {}
    if isinstance(profilers, list):
        for p in profilers:
            _keys = get_profiler_keys(p)
            for k,v in _keys.items():
                if k in keys:
                    keys[k] += v
                else:
                    keys[k] = v

    elif isinstance(profilers, Profiler) or issubclass(profilers, Profiler):
        _keys = get_profiler_keys( profilers)
        for k, v in _keys.items():
            if k in keys:
                keys[k] += v
            else:
                keys[k] = v

    return keys


def get_profiler_keys(profiler):

    if isinstance(profiler, str):
        profiler = import_from_string(profiler)

    keys={}
    if inspect.isclass(profiler):
        profiler = profiler()

    if isinstance(profiler, ColumnProfilerSet) or isinstance(profiler, ColumnProfiler):
        keys['column'] = profiler.profiler_keys()

    elif isinstance(profiler, TableProfilerSet) or isinstance(profiler, TableProfiler):
        keys['table'] = profiler.profiler_keys()

    return keys


