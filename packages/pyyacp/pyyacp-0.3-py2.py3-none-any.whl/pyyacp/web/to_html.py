
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

PATH = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates'))
)



def to_html(table, cnt, dir):
    m_order=['data_type','data_class','patterns',
             'stats_num_rows','stats_distinct','stats_empty',
             'stats_min_len','stats_mean_len','stats_max_len',
             'stats_constancy','stats_uniqueness','stats_top_value',
             'c_dist_dist','benford_is','benford_chi','benford_dist']
    output = os.path.join('.', "../html/{}.html".format(cnt))
    with open(output, "w") as f:
        template = env.get_template('profile.jinja')
        f.write(template.render(
            basic=table.table_structure(),
            columnIDs=table.columnIDs,
            tmeta=table.meta,
            m_order=m_order,
            comments=table.comments,
            data=table.data.head(5).to_html(classes='ui celled table'),
            meta=table.colum_profiles().to_dict(orient='index')#table.describe_colmeta().to_html(classes='ui celled table')
        ))

col_profile_keys = ['uri', 'digest', 'col',
          'stats_mean_len', 'stats_max_len', 'stats_distinct', 'stats_constancy', 'stats_min_len', 'stats_max_value',
          'stats_min_value',
          'data_type', 'patterns', 'stats_empty', 'stats_num_rows', 'benford_dist', 'stats_uniqueness', 'c_dist_dist',
          'benford_is', 'benford_chi', 'stats_top_value', 'data_class']


_table_structure=['uri','rows','columns','headers','comments','comment_lines','header_lines']
_table_profile = ['encoding', 'uri', 'filename', 'delimiter', 'quotechar', 'lineterminator', 'skipinitialspace',
                          'quoting', 'delimiter', 'doublequote', 'fd']

def to_html_string(table, sample=5):
    # table_meta={}
    col_profiles={}
    # for k, v in table.table_profile().items():
    #     table_meta[k] = v
    # for k, v in table.table_structure().items():
    #     table_meta[k] = v
    #
    for col, meta in table.colum_profiles().to_dict().items():
         col_profiles[col] = {k: meta[k] for k in col_profile_keys if k in meta}
    #
    t_c_p = {}
    for col, profile in col_profiles.items():
         for k, v in profile.items():
             if k != 'col':
                 d = t_c_p.setdefault(k, {})
                 d[col] = v
    # t_s = {k: v for k, v in table_meta.items() if k in _table_structure}
    # t_p = {k: v for k, v in table_meta.items() if k in _table_profile}
    #
    # t1 = table
    # t1_s = t_s
    # t1_p = t_p
    # t1_c_p = t_c_p
    #
    #
    if sample:
        data=    [list(table.data.columns)] + [list(row) for idx, row in table.data.head(sample).iterrows()]
    else:
        data = [list(table.data.columns)] + [list(row) for idx, row in table.data.iterrows()]

    html_data = {
        'basic':table.table_structure(),
        'columnIDs':table.columnIDs,
        'tmeta':table.meta,
        'comments':table.comments,
        'data':data,
        'meta':t_c_p
    }

    template = env.get_template('profile.jinja')
    return template.render(**html_data)
