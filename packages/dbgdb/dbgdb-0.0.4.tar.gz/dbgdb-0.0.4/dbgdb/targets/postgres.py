#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/18/18
"""
.. currentmodule:: dbgdb.targets.postgres
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains PostgreSQL targets.
"""
import luigi
from ..db.postgres import connect, schema_exists


class PgSchemaTarget(luigi.Target):
    """
    This is a target that represents a file geodatabase (GDB).
    """
    def __init__(self,
                 url: str,
                 schema: str,
                 dne: bool = False):
        """

        :param url: the path to the file GDB
        :param schema: the target schema
        :param dne: ("does not exist") this should be `True` if the target's
            task is considered to be complete if the schema does not exist
        """
        super().__init__()
        self._url: str = url
        self._schema: str = schema
        self._dne: bool = dne

    def exists(self) -> bool:
        """
        Does the file target schema exist?

        :return: `True` if the file geodatabase exists, otherwise `False`
        """
        # First, we need to determine whether or not the schema exists.
        _exists = schema_exists(url=self._url, schema=self._schema)
        # This next part is where it gets just a little tricky:  If this target
        # is the result of a task that was supposed to, for example, drop the
        # schema, the task may be considered to have been completed if the
        # schema does not exist.
        if self._dne:
            return not _exists
        # Otherwise, we can just give the more intuitive answer.
        return _exists

    def connect(self):
        """
        Get a connection to the database.

        :return: a connection to the database
        """
        return connect(url=self._url)
