import functools

from dtpattern.dtpattern1 import pattern_comparator, aggregate_patterns, translate
from pyyacp.profiler import ColumnProfiler, ColumnByCellProfiler, is_not_empty
from pyyacp.timer import timer


class ColumnPatternProfiler(ColumnProfiler,ColumnByCellProfiler):

    def __init__(self, num_patterns=3):
        super(ColumnPatternProfiler, self).__init__('cpp','patterns')
        self.num_patterns=num_patterns
        self.patterns=[]
        self.pa = self.patterns.append

#    @timer(key="cpp_column")
#    def profile_column(self, column, meta):
#        return dtpattern.aggregate(filter(is_not_empty,column), size=self.num_patterns)

    @timer(key="cpp_result")
    def result(self):
        p = sorted(self.patterns, key=functools.cmp_to_key(pattern_comparator))
        #empty
        #reset in case there is another column
        self.patterns = []
        self.pa = self.patterns.append
        return aggregate_patterns(p, size=self.num_patterns)

    def accept(self, cell):
        if is_not_empty(cell):
            self.pa(translate(cell))
