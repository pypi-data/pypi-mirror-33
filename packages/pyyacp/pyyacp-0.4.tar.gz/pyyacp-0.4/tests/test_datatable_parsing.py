import pytest
from pyyacp.datatable import parseDataTables


t1=[['A','B','C'],
    ['1','2','3'],
    ['2','3','4']
    ]
t2=[
    ['A', 'B'],
    ['1', '2'],
    ['2', '3'],
]


testdata=[ t1,t2]
@pytest.mark.parametrize("table", testdata)
def test_simple(table):

    csvreader=table

    tables = parseDataTables(csvreader)
    assert len(tables) ==1
    table = tables[0]
    assert table.no_cols == len(csvreader[0])
    assert table.no_rows == len(csvreader)-1
    assert len(table.header_rows) == 1
    assert len(table.comment_rows) == 0

t1=[['6','5','1'],
    ['1','2','3'],
    ['2','3','4']
    ]
t2=[
    ['2', '4'],
    ['1', '2'],
    ['2', '3'],
]


testdata=[ t1,t2]
@pytest.mark.parametrize("table", testdata)
def test_simple_noheader(table):

    csvreader=table
    tables = parseDataTables(csvreader)
    assert len(tables) ==1
    table = tables[0]
    assert table.no_cols == len(csvreader[0])
    assert table.no_rows == len(csvreader)
    assert len(table.header_rows) == 0
    assert len(table.comment_rows) == 0


t1=[
    ['Comment'],
    ['6','5','1'],
    ['1','2','3'],
    ['2','3','4']
    ]
t2=[
    ['Comment'],
    ['2', '4'],
    ['1', '2'],
    ['2', '3'],
]


testdata=[ t1,t2]
@pytest.mark.parametrize("table", testdata)
def test_simple_comment_no_header(table):

    csvreader=table
    tables = parseDataTables(csvreader)
    assert len(tables) == 1
    table = tables[0]
    assert table.no_cols == len(csvreader[1])
    assert table.no_rows == len(csvreader)-1
    assert len(table.header_rows) == 0
    assert len(table.comment_rows) == 1

def test_two_tables():
    csvreader = [
        ['A', 'B', 'C'],
        ['1', '2', '3'],
        ['2', '3', '4'],
        ['A', 'B'],
        ['1', '2'],
        ['2', '3'],

    ]
    tables = parseDataTables(csvreader)
    assert len(tables) == 2
    table = tables[0]
    assert table.no_cols == 3
    assert table.no_rows == 2
    assert len(table.header_rows) == 1


def test_two_tables_with_comments_empty_line():
    csvreader = [
        ['This is a comment'],
        ['2', '3', '4'],
        ['1', '2', '3'],
        ['2', '3', '4'],
        [],
        ['A', 'B'],
        ['1', '2'],
        ['2', '3'],

    ]
    tables = parseDataTables(csvreader)
    assert len(tables) == 2

    table = tables[0]
    assert table.no_cols == 3
    assert table.no_rows == 3
    assert len(table.header_rows) == 0
    assert len(table.comment_rows) == 1


    table = tables[1]
    assert table.no_cols == 2
    assert table.no_rows == 2
    assert len(table.header_rows) == 1
    assert len(table.comment_rows) == 0

