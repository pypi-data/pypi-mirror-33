import inspect

from pyjuhelpers.module_import import import_from_string
from pyyacp.config import pyyacpconfig, my_import
from pyyacp.datatable import parseDataTables
from pyyacp.profiler import Profiler, ColumnProfilerSet, ColumnProfiler, TableProfilerSet, TableProfiler
from pyyacp.profiler.profiling import get_profilers_keys, apply_profilers

from pyyacp.profiler.column_stats_profiler import ColumnStatsProfiler
from pyyacp.profiler.fdprofiler import FDProfiler
from pyyacp.profiler.cset_detection import CharacterSetProfiler
from pyyacp.profiler.colum_pattern_profiler import ColumnPatternProfiler
from pyyacp.profiler.data_type_detection import DataTypeDetection
from pyyacp.profiler.datatype_interpretation import DataTypeInterpretation
from pyyacp.profiler.distributions import CharacterDistributionProfiler
from pyyacp.profiler.distributions import BenfordsLawDistribution

from tests import create_dummy_table


def _test_profilers(table, profilers, capsys):



    ptable = apply_profilers(table, profilers=profilers)

    if isinstance(profilers, list):
        for p in profilers:
            _test_profiler(ptable   , p,capsys)
    elif isinstance(profilers, str) or isinstance(profilers, Profiler) or issubclass(profilers, Profiler):
        _test_profiler(ptable, profilers,capsys)

def _test_profiler(ptable , profiler,capsys):
    if isinstance(profiler , str):
        profiler = import_from_string(profiler)


    if inspect.isclass(profiler):
        profiler = profiler()

    if isinstance(profiler, ColumnProfilerSet) or isinstance(profiler, ColumnProfiler):

        meta = ptable.column_metadata
        for k, m in meta.items():
            for k in profiler.profiler_keys():
                assert k in m
                assert k in ptable.profiler_keys['column']
                with capsys.disabled():
                    print("{} -> {}".format(k, m[k]))


    elif isinstance(profiler, TableProfilerSet) or isinstance(profiler, TableProfiler):
        meta = ptable.table_metadata
        for k in profiler.profiler_keys():
            assert k in meta
            assert k in ptable.profiler_keys['table']
            with capsys.disabled():
                print("{} -> {}".format(k, meta[k]))


def _setup_table(tmpdir):
    d = tmpdir.mkdir("data")
    csv1 = str(d.join("table1.csv"))
    create_dummy_table(csv1)

    return csv1

def _parse_table(tmpdir,capsys):
    csv1 = _setup_table(tmpdir)


    table = parseDataTables(csv1, max_tables=1)

    with capsys.disabled():
        print(table.data.head(5))

    return table

def test_column_stats_profiler(tmpdir,capsys):

    table= _parse_table(tmpdir,capsys)

    profiler = ColumnStatsProfiler

    _test_profilers(table, profiler, capsys)

def test_FD_PROFILER(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    profiler = FDProfiler

    _test_profilers(table, profiler,capsys)


def test_CharacterSetProfiler(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    profiler = CharacterSetProfiler

    _test_profilers(table, profiler,capsys)


def test_ColumnPatternProfiler(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    profiler = ColumnPatternProfiler

    _test_profilers(table, profiler,capsys)


def test_DataTypeDetection(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)


    profiler = DataTypeDetection

    _test_profilers(table, profiler,capsys)


def test_DataTypeInterpretation(tmpdir, capsys):
    table = _parse_table(tmpdir, capsys)

    profiler = DataTypeInterpretation

    _test_profilers(table, profiler, capsys)


def test_CharacterDistributionProfiler(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)


    profiler = CharacterDistributionProfiler

    _test_profilers(table, profiler,capsys)


def test_BenfordsLawDistribution(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    profiler = BenfordsLawDistribution

    _test_profilers(table, profiler,capsys)




def test_all(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    profilers = [BenfordsLawDistribution

                ,CharacterDistributionProfiler
                ,DataTypeDetection
                ,ColumnPatternProfiler
                ,CharacterSetProfiler
                ,FDProfiler
                ,ColumnStatsProfiler
    ]

    _test_profilers(table, profilers,capsys)


def test_config_all(tmpdir,capsys):
    table = _parse_table(tmpdir,capsys)

    _test_profilers(table, pyyacpconfig.DEFAULT_PROFILERS,capsys)



def test_get_all_keys():
    profilers = [BenfordsLawDistribution

        , CharacterDistributionProfiler
        , DataTypeDetection
        , ColumnPatternProfiler
        , CharacterSetProfiler
        , FDProfiler
        , ColumnStatsProfiler
                 ]

    keys= get_profilers_keys(profilers)
    for p in profilers:
        p=p()
        for k in p.profiler_keys():
            if isinstance(p,TableProfiler):
                assert k in keys['table']
            elif isinstance(p,ColumnProfiler):
                assert k in keys['column']





