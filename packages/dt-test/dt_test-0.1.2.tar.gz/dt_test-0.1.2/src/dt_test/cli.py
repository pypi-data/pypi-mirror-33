# -*- coding: utf-8 -*-
"""Console script for dt_test."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for dt_test."""

    click.echo("test addtional data")
    with open('deps/miner.txt', 'r') as f:
        mdata = f.read()
        click.echo(mdata)
    click.echo("Replace this message by putting your code into "
               "dt_test.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
