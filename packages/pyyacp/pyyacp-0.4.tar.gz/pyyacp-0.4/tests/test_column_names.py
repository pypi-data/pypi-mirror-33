from pyyacp.datatable import create_column_names


def test_basic():

    rows= [['A','B','C']]
    names = create_column_names(rows)

    h_transposed = list(map(list, zip(*rows)))
    for i, hs in enumerate(h_transposed):
        if 'miss' in names[i]:
            assert all(h is None or len(h.strip()) > 0 for h in hs)
        else:
            assert names[i] in hs

def test_missing():

    rows= [['A',None,'C']]
    names = create_column_names(rows)

    h_transposed = list(map(list, zip(*rows)))
    for i, hs in enumerate(h_transposed):
        if 'miss' in names[i]:
            assert all(h is None or len(h.strip()) > 0 for h in hs)
        else:
            assert names[i] in hs


def test_multi():

    rows= [['A',None,'C'],['a','b','c']]
    names = create_column_names(rows)

    h_transposed = list(map(list, zip(*rows)))
    for i, hs in enumerate(h_transposed):
        if 'miss' in names[i]:
            assert all(h is  None or len(h.strip()) > 0 for h in hs)
        else:
            assert names[i] in hs

def test_multi():

    rows= [['A',None,'C'],['','b','c']]
    names = create_column_names(rows)

    h_transposed = list(map(list, zip(*rows)))
    for i, hs in enumerate(h_transposed):
        if 'miss' in names[i]:
            assert all(h is  None or len(h.strip()) > 0 for h in hs)
        else:
            assert names[i] in hs

def test_duplciates():

    rows= [['A',None,'A']]
    names = create_column_names(rows)

    h_transposed = list(map(list, zip(*rows)))
    for i, hs in enumerate(h_transposed):
        if 'miss' in names[i]:
            assert all(h is  None or len(h.strip()) > 0 for h in hs)
        else:
            assert names[i] in hs