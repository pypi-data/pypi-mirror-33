from pyyacp import YACParser
from pyyacp import datatable
from pyyacp.cli import inspect
from pyyacp.table_structure_helper import AdvanceStructureDetector

filename="/Users/jumbrich/new_folder/dev/tablerec/tablerec/library_data.csv"
filename=None
url='http://data.wu.ac.at/data/unibib/library_data.csv'



#import requests
#r = requests.get(url)
#iter_lines = [line for line in r.iter_lines(chunk_size=1024)]
#split_lines = r.content.splitlines()


def my_iter_lines(result):
    buf = b''
    for chunk in result.iter_content(chunk_size=64 * 1024, decode_unicode=False):
        buf += chunk
        pos = 0
        while True:
            eol = buf.find(b'\n', pos)
            if eol != -1:
                yield buf[pos:eol]
                pos = eol + 1
            else:
                buf = buf[pos:]
                break
    if buf:
        yield buf

#iter1_lines=[line for line in my_iter_lines(r)]
#print(len(iter_lines), len(split_lines), len(iter1_lines))
#import sys
#sys.exit(0)

filename='/Users/jumbrich/new_folder/data/catalog/data/data.wu.ac.at/75/L2RhdGEvdW5pYmliL2xpYnJhcnlfZGF0YS5jc3Y=/b48f86a2552739bf4e0503ff7ba64cd1.gz'


url=None
import os
#print(os.stat(filename))
#print(os.path.isfile(filename))
print(open(filename))
structure_detector = AdvanceStructureDetector()
sample_size = 1800

yacp = YACParser(filename=filename, url=url, structure_detector=structure_detector, sample_size=sample_size)
if url is None:
    url = 'http://example.org/table'
tables = datatable.parseDataTables(yacp, url=url, max_tables=10)

for table in tables:
    table.print_summary()
