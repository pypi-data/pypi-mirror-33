# -*- coding: utf-8 -*-

"""Console script for pyyacp."""
import sys
import click

from pyyacp import datatable
from pyyacp.profiler.profiling import apply_profilers
from pyyacp.table_structure_helper import AdvanceStructureDetector

from pyyacp import YACParser

import click

from pyyacp.web.to_html import to_html_string


class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
            ' NOTE: This argument is mutually exclusive with %s' %
            self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        other_present = self.not_required_if in opts

        if other_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, self.not_required_if))
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)

@click.group()
def cli():
    """Console script for pyyacp."""
    pass

@cli.command()
@click.option('-f','--file',  help='File', cls=NotRequiredIf, not_required_if='url')
@click.option('-u','--url',  help='URL'  , cls=NotRequiredIf, not_required_if='file')
def inspect(file, url):
    """Inspect a CSV file to figure out about the dialect, comment and header lines and the overall structure."""

    structure_detector = AdvanceStructureDetector()
    sample_size = 1800

    click.echo("Input filename:{}, ur:{}".format(file, url))
    yacp = YACParser(filename=file, url=url, structure_detector=structure_detector, sample_size=sample_size)
    if url is None:
        url = 'http://example.org/table'
    tables = datatable.parseDataTables(yacp, url=url, max_tables=10)

    click.echo("Found {} tables".format(len(tables)))
    for table in tables:
        table.print_summary()
    return 0

@cli.command()
@click.option('-f','--file',  help='File', cls=NotRequiredIf, not_required_if='url')
@click.option('-u','--url',  help='URL'  , cls=NotRequiredIf, not_required_if='file')
def clean(file, url):
    """Parse and clean a CSV file (strip comments, utf-8 encoding, default dialect"""


    structure_detector = AdvanceStructureDetector()
    sample_size = 1800

    click.echo("Input filename:{}, ur:{}".format(file, url))
    yacp = YACParser(filename=file, url=url, structure_detector=structure_detector, sample_size=sample_size)

    if url is None:
        url = 'http://example.org/table'
    tables = datatable.parseDataTables(yacp, url=url, max_tables=10)

    if len(tables)>1:
        click.echo("Found {} tables".format(len(tables)))
    else:
        print(tables[0].generate())

@cli.command()
@click.option('-f','--file',  help='File', cls=NotRequiredIf, not_required_if='url')
@click.option('-u','--url',  help='URL'  , cls=NotRequiredIf, not_required_if='file')
@click.option('--html',  help='html representation',type=click.Path(resolve_path=True))
@click.option('-l','--load',  help='try to open/load html file',count=True)
@click.option('-s','--sample',  help='sample rows',type=int, default=None)

def profile(file, url, html, load, sample):
    """Console script for pyyacp."""

    structure_detector = AdvanceStructureDetector()
    sample_size = 1800
    max_tables=1


    click.echo("Input filename:{}, ur:{}".format(file, url))
    yacp = YACParser(filename=file, url=url, structure_detector=structure_detector, sample_size=sample_size)
    if url is None:
        url='http://example.org/table'
    tables = datatable.parseDataTables(yacp, url=url, max_tables=max_tables)

    if max_tables==1:
        table=tables
    elif len(tables)>1:
        click.echo("Found {} tables".format(len(tables)))
        return


    apply_profilers(table)


    if html:
        click.echo("Writing HTML representation to {}".format(click.format_filename(html)))
        with open(html, "w") as f:
            f.write(to_html_string(table,sample=sample))
        if load:
            click.launch(html)
    else:
        table.print_summary()

if __name__ == "__main__":
    cli() # pragma: no cover
