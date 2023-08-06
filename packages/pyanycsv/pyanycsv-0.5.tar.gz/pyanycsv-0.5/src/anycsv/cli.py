# -*- coding: utf-8 -*-

"""Console script for pyyacp."""

import anycsv
import sys
import click
from pyjuhelpers.logging import *

import logging

from pyjuhelpers.timer import Timer

logging.basicConfig(level=logging.INFO)
@click.group()
@click.option('-v', '--verbose', count=True, help="-v INFO, -vv DEBUG, -vvv Default and file debug")
def main(verbose):

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


@main.command('inspect')
@click.argument('csv')#, help="Input CSV file, either from file or URL")
@click.option('-b', '--bench',  is_flag=True)
@click.option('--bench_out', help="file to dump benchmark", type=click.Path())
def inspect_csv(csv, bench,bench_out):
    """Inspect a CSV file to figure out about the dialect, comment and header lines and the overall structure."""

    click.echo("Input CSV {}".format(csv))

    reader = anycsv.reader(csv)
    for i,row in enumerate(reader):
        pass

    click.echo("{:-^80}".format(" Table Info "))
    click.echo("    input: {}".format(reader.csv))
    click.echo(" encoding: {}".format(reader.encoding))
    click.echo("      md5: {}".format(reader.digest))
    click.echo("  dialect:")
    for k,v in reader.dialect._asdict().items():
        click.echo("    {}: {}".format(k,v))

    if bench:
        click.echo("TIMING")
        click.echo(Timer.printStats())
    if bench_out:
        Timer.to_csv(bench_out)

@main.command('parse')
@click.argument('csv')#, help="Input CSV file, either from file or URL")
@click.option('-o','--out')#, help="Output csv file")
@click.option('-b', '--bench',  is_flag=True)
@click.option('--bench_out', help="file to dump benchmark", type=click.Path())
def parse_csv(csv, out, bench, bench_out):
    """Inspect a CSV file to figure out about the dialect, comment and header lines and the overall structure."""

    click.echo("Input CSV {}".format(csv))

    table = anycsv.reader(csv)

    if out:
        fout = open(out, "wt")
    else:
        fout=sys.stdout

    import csv
    writer = csv.writer(fout)

    for row in table:
        writer.writerow(row)

    if out:
        fout.close()

    if bench:
        click.echo("TIMING")
        click.echo(Timer.printStats())
    if bench_out:
        Timer.to_csv(bench_out)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
