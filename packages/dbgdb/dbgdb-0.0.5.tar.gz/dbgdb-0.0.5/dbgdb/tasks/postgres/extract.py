#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/20/18
"""
.. currentmodule:: dbgdb.tasks.extract
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains the :py:class:`ExtractTask` task which you can use to
extract data from your database instance.
"""
from pathlib import Path
from typing import cast
import luigi
from dbgdb.ogr.postgres import extract, OgrDrivers


class PgExtractTask(luigi.Task):
    """
    This task loads a file geodatabase into a database instance.

    :cvar url: the URL of the target database
    :cvar schema: the target schema
    :cvar outdata: the path to which data should be exported
    :cvar driver: the driver to use for exporting data
    """
    url: luigi.Parameter = luigi.Parameter(
        default='postgresql://postgres@localhost:5432/postgres',
        description='the URL of the database instance'
    )
    schema: luigi.Parameter = luigi.Parameter(
        default='imports',
        description='the target schema into which data is loaded'
    )
    outdata: luigi.Parameter = luigi.Parameter(
        description='the path to which you want to export your data'
    )
    driver: luigi.Parameter = luigi.EnumParameter(
        enum=OgrDrivers,
        default=OgrDrivers.Spatialite,
        description='the export driver to use'
    )

    def requires(self):
        """
        This task has no requirements.

        :return: an empty iteration
        """
        return []

    def output(self) -> luigi.LocalTarget:
        """
        This task returns a :py:class:`PgSchemaTarget` that points to the
        target schema where the GDB was loaded.

        :return: the PostgreSQL schema target
        """
        return luigi.LocalTarget(path=str(self.outdata))

    def run(self):
        """
        Run the task.
        """
        outdata_path = Path(str(self.outdata))
        extract(outdata=outdata_path,
                url=str(self.url),
                schema=str(self.schema),
                driver=cast(OgrDrivers, self.driver))
