# -*- coding: utf-8 -*-

"""Console script for pyyacp."""

from pyyacp.datatable import parseDataTables

from pyyacp.profiler.profiling import apply_profilers

import click

from pyyacp.web.to_html import to_html_string

from pyjuhelpers.logging import *
from pyjuhelpers.timer import Timer


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

import logging
logging.basicConfig(level=logging.INFO)
@click.group()
@click.option('-v', '--verbose', count=True, help="-v INFO, -vv DEBUG")
def cli(verbose):

    if verbose == 0:
        click.echo("Default logging")
        logging.config.dictConfig(defaultConf)
    elif verbose == 1:
        logging.config.dictConfig(infoConf)
        click.echo("Info logging")
    elif verbose == 2:
        click.echo("Debug logging")
        logging.config.dictConfig(debugConf)
    else:
        click.echo("Default & File logging")
        logging.config.dictConfig(fileConf)

    pass

@cli.command()
@click.argument("csv")
@click.option('-b', '--bench',  is_flag=True)
def inspect(csv, bench):
    """Inspect a CSV file to figure out about the dialect, comment and header lines and the overall structure."""

    tables = parseDataTables(csv)

    click.echo("Found {} tables".format(len(tables)))
    for i,table in enumerate(tables):
        click.echo("Table-{}".format(i))
        table.print_summary()

    if bench:
        click.echo("TIMING")
        click.echo(Timer.printStats())


@cli.command()
@click.argument("csv")
@click.option('-b', '--bench',  is_flag=True)
@click.option('--bench_out', help="file to dump benchmark", type=click.Path())
def clean(csv, bench, bench_out):
    """Parse and clean a CSV file (strip comments, utf-8 encoding, default dialect"""


    tables = parseDataTables(csv)

    if len(tables)>1:
        click.echo("Found {} tables".format(len(tables)))
    else:
        print(tables[0].generate())

    if bench:
        click.echo("TIMING")
        click.echo(Timer.printStats())
    if bench_out:
        Timer.to_csv(bench_out)

@cli.command()
@click.argument("csv")
@click.option('--html',  help='html representation',type=click.Path(resolve_path=True))
@click.option('-l','--load',  help='try to open/load html file',count=True)
@click.option('-s','--sample',  help='sample rows',type=int, default=5)
@click.option('-b', '--bench',  is_flag=True)
@click.option('--bench_out', help="file to dump benchmark", type=click.Path())
def profile(csv, html, load, sample, bench, bench_out):
    """Console script for pyyacp."""

    tables = parseDataTables(csv)

    click.echo("Found {} tables".format(len(tables)))
    for table in tables:
        ptable = apply_profilers(table)

        if html:
            click.echo("Writing HTML representation to {}".format(click.format_filename(html)))
            with open(html, "w") as f:
                f.write(to_html_string(ptable,sample=sample))
            if load:
                click.launch(html)
        else:
            ptable.print_summary()

    if bench:
        click.echo("TIMING")
        click.echo(Timer.printStats())
    if bench_out:
        Timer.to_csv(bench_out)

if __name__ == "__main__":
    cli() # pragma: no cover
