#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: dbgdb.cli
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is the entry point for the command-line interface (CLI) application.  It
can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.
"""
import multiprocessing
from typing import Iterable
import click
import luigi
from luijo.config import find_configs
from dbgdb.tasks.postgres.drop import PgDropSchemaTask
from dbgdb.tasks.postgres.extract import PgExtractTask
from dbgdb.tasks.postgres.load import PgLoadTask


class Info(object):
    """
    This is an information object that can be used to pass data between CLI
    functions.
    """
    def __init__(self):  # Note that this object must have an empty constructor.
        self.local: bool
        self.workers: int
        self.config: str


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(
    Info,
    ensure=True
)


# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group()
@click.option('-l', '--local', is_flag=True)
@click.option('--workers',
              type=int,
              default=multiprocessing.cpu_count(),
              help='the number of workers (defaults to the CPU count)')
@pass_info
def cli(info: Info,
        local: bool,
        workers: int):
    """
    Run tasks in this library.
    """
    info.local = local
    info.workers = workers


def run(tasks: Iterable[luigi.Task], info: Info):
    """
    Run tasks on the local scheduler.

    :param tasks: the tasks to run
    :param info: the :py:class:`Info` object containing other parameters
    """
    params = {
        'workers': info.workers
    }
    if info.local:
        params['no_lock'] = False
        params['local_scheduler'] = True

    luigi.build(
        list(tasks),
        **params
    )


@cli.command()
@click.option('-u', '--url',
              default='postgresql://postgres@localhost:5432/gis',
              help='the URL of the database instance')
@click.option('-s', '--schema',
              default='imports',
              help='the target schema')
@click.argument('indata', type=click.Path(exists=True))
@pass_info
def load(info: Info, url: str, schema: str, indata: str):
    """
    Load data into a database instance.
    """
    task = PgLoadTask(url=url, schema=schema, indata=indata)
    run([task], info)


@cli.command()
@click.option('-u', '--url',
              default='postgresql://postgres@localhost:5432/gis',
              help='the URL of the database instance')
@click.option('-s', '--schema',
              default='imports',
              help='the schema that contains the data')
@click.argument('outdata', type=click.Path(exists=False))
@pass_info
def extract(info: Info, url: str, schema: str, outdata: str):
    """
    Extract data from a database instance.
    """
    task = PgExtractTask(url=url, schema=schema, outdata=outdata)
    run([task], info)


@cli.command()
@click.option('-u', '--url',
              default='postgresql://postgres@localhost:5432/gis',
              help='the URL of the database instance')
@click.argument('what', type=click.Choice(['database', 'schema']))
@click.argument('name', type=str)
@pass_info
def drop(info: Info, url: str, what: str, name: str):
    """
    Drop a database or schema.
    """
    task: luigi.Task = None
    if what == 'database':
        click.echo('NOT IMPLEMENTED YET')
    elif what == 'schema':
        task = PgDropSchemaTask(url=url, schema=name)
    # Run the task.
    run([task], info)


@cli.command()
def findcfg():
    """
    Find the Luigi configuration files on the system.
    """
    candidates = find_configs()
    if not candidates:
        click.echo(
            click.style(
                'No candidate config files were found.',
                fg='yellow')
        )
    else:
        for candidate in candidates:
            click.echo(click.style(candidate, fg='blue'))
