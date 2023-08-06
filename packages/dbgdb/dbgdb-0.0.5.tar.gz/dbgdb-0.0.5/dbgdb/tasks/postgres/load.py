#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/21/18
"""
.. currentmodule:: dbgdb.tasks.load
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains the :py:class:`LoadTask` task which you can use to
load a file geodatabase into your database instance.
"""
from pathlib import Path
import luigi
from dbgdb.targets.postgres import PgSchemaTarget
from dbgdb.ogr.postgres import load


class PgLoadTask(luigi.Task):
    """
    This task loads a file geodatabase into a database instance.

    :cvar url: the URL of the target database
    :cvar schema: the target schema
    :cvar indata: the path to the input data
    """
    url: luigi.Parameter = luigi.Parameter(
        default='postgresql://postgres@localhost:5432/postgres',
        description='the URL of the database instance'
    )
    schema: luigi.Parameter = luigi.Parameter(
        default='imports',
        description='the target schema into which data is loaded'
    )
    indata: luigi.Parameter = luigi.Parameter(
        description='the path to the data you want to import'
    )

    def requires(self):
        """
        This task has no requirements.

        :return: an empty iteration
        """
        return []

    def output(self) -> PgSchemaTarget:
        """
        This task returns a :py:class:`PgSchemaTarget` that points to the
        target schema where the data was loaded.

        :return: the PostgreSQL schema target
        """
        return PgSchemaTarget(url=str(self.url), schema=str(self.schema))

    def run(self):
        """
        Run the task.
        """
        input_path = Path(str(self.indata))
        load(
            indata=input_path,
            url=str(self.url),
            schema=str(self.schema),
            overwrite=True,
            progress=False,
            use_copy=True
        )
