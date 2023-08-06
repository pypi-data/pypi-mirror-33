from dtpattern.dtpattern1 import pattern
from pyyacp.profiler import ColumnProfiler
from pyjuhelpers.timer import timer

class ColumnPatternProfiler(ColumnProfiler):

    def __init__(self):
        super(ColumnPatternProfiler, self).__init__('cpp','pattern')

    def result_datatype(self):
        return str

    @timer(key="profile.col_pattern")
    def _profile_column(self, values, meta) -> str:
        res= pattern(values, includeCount=False)
        if len(res)>0:
            return res[0]



