# -*- coding: utf-8 -*-

"""Console script for dtpattern."""

import click

from dtpattern.dtpattern1 import pattern


@click.group()
def dtpattern():
    """dtpattern cli , generate patterns for a set of values"""
    pass

@dtpattern.command()
@click.argument('items', nargs=-1)
@click.option('--size', type=int, default=1)
@click.option('--raw', count=True)
@click.option('-v', '--verbose', count=True)
def items(items, verbose, raw, size):
    """read values from cli"""

    if verbose:
        click.echo("Item list {}".format(items))

    res= pattern(items, size=1, includeCount=not raw, verbose=verbose)

    if verbose:
        click.echo("Result(s):")
    for r in res:
        click.echo(" {}".format(r))

@dtpattern.command()
@click.argument('file',  type=click.File('r'))
@click.option('--size', type=int, default=1)
@click.option('--raw', count=True)
@click.option('-v', '--verbose', count=True)
def file(file, verbose, raw, size):
    """read values from a file"""

    items=file.read().splitlines()
    if verbose:
        click.echo("Item list {}".format(items))

    res= pattern(items, size=1, includeCount=not raw, verbose=verbose)

    if verbose:
        click.echo("Result(s):")
    for r in res:
        click.echo(" {}".format(r))



