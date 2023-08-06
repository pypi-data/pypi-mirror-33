#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import


import os
import logging
import json

from csvmimesis import __version__
from csvmimesis.mimesis_data_providers import print_mimesis,print_unique, print_locals
from csvmimesis.table_generator import create_table, write_table,print_table, write_tables,create_table_pair,print_tables

__author__ = "jumbrich"
__copyright__ = "jumbrich"
__license__ = "mit"

_logger = logging.getLogger(__name__)

import sys
import click


@click.group()
@click.option('-v', '--verbose', count=True)
def main(verbose):
    click.echo(verbose)
    if verbose == 1:
        logging.basicConfig(level=logging.INFO)
    if verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
def list_locals():
    click.echo("Available locals")
    print_locals()


@main.command()
@click.option("-p","--provider", default=None)
def list_all(provider):
    click.echo("Available providers and methods")
    print_mimesis(provider=provider)

@main.command()
@click.option("-p","--provider", default=None)
@click.option("-m","--method", default=None)
@click.option("-l","--local", default=None)
@click.option("--max", default=1000, type=int)
def unique(provider, method, local, max):
    if provider:
        if method:
            click.echo("Number of unique values for provider [{}] and methods (max_unique={} )".format(provider,max))
        else:
            click.echo("Number of unique values for provider [{}] and method [{}] (max_unique={} )".format(provider, method, max))
    else:
        click.echo("Number of unique values for each providers and methods (max_unique={} )".format(max))
    print_unique(provider=provider, method=method, local=local, max=max)

@main.command()
@click.option("-r","--rows", default=10, help="Number of rows, default =10")
@click.option("-p","--providers", default=None,multiple=True)
@click.option("-l","--local", default=None)
@click.option("-t","--template", default=None, type=click.Path(resolve_path=True))
@click.option("-f","--file", default=None, type=click.Path(resolve_path=True))
@click.option("-d","--dir", default=None, type=click.Path(resolve_path=True))
@click.option("--print", default=False)
def table(providers,  local, rows, template, dir, file, print):
    import json

    table=None
    if template:
        table= json.load(open(template))

    elif providers:
        table={
                "prefix":None,
                "local":local,
                "rows": rows,
                "columns": [c for c in providers]
            }

    _tab = create_table(table)
    if print:
        print_table(_tab)
    write_table(_tab, dir, file)

@main.command()
@click.option("-t","--template", default=None, type=click.Path(resolve_path=True))
@click.option("--prefix", default=None, type=click.Path(resolve_path=True))
@click.option("-d","--dir", default=None, type=click.Path(resolve_path=True))
@click.option("-p","--print", default=False)
def tables(template, dir, prefix, print):

    tables= json.load(open(template))

    for tab_profile in tables:
        _tab = create_table(tab_profile)
        _prefix = tab_profile.get("prefix") if "prefix" in tab_profile else prefix
        if print:
            print_tables(_tab)
        write_table(_tab, prefix=_prefix, dir=dir)

@main.command()
@click.option("-t","--template", default=None, type=click.Path(resolve_path=True))
@click.option("-d","--dir", default=None, type=click.Path(resolve_path=True), required=True)
@click.option("-p","--print", default=False)

def table_pairs(template, dir, print):

    t_pairs= json.load(open(template))

    for tp in t_pairs:
        local=tp.get('local',None)
        shared_providers=tp.get('shared_providers',None)
        add_providers=tp.get('add_providers',None)
        join_providers=tp.get('join_providers',None)
        rows=tp['rows']


        _tables = create_table_pair(shared_providers=shared_providers,
                                    add_providers=add_providers,
                                    join_providers=join_providers,
                                    rows=rows, local=local)

        if print:
            print_tables(_tables)

        _dir = os.path.join(dir,tp['prefix'])
        write_tables(_tables, dir=_dir, prefix=tp['prefix'])

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
