
from jinja2 import Environment, FileSystemLoader
import os

PATH = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates'))
)

def to_html_string(table, sample=5):


    if sample:
        data = [list(table.data.columns)] + [list(row) for idx, row in table.data.head(sample).iterrows()]
    else:
        data = [list(table.data.columns)] + [list(row) for idx, row in table.data.iterrows()]

    _table = {
        'profiledata':table.profiledata(),
        'table':table,
        'sample':data
    }

    template = env.get_template('profile_view.jinja')
    return template.render(table=_table)
