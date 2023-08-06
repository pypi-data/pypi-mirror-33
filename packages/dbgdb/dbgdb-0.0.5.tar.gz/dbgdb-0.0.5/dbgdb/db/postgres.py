#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 5/19/18
"""
.. currentmodule:: postgres
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains utility functions to help when working with PostgreSQL
databases.
"""
# pylint: disable=no-member
import json
from pathlib import Path
from urllib.parse import urlparse, ParseResult
from typing import Iterable
from addict import Dict
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Load the Postgres phrasebook.
sql_phrasebook = Dict(
    json.loads(
        (
            Path(__file__).resolve().parent / 'postgres.json'
        ).read_text()
    )['sql']
)


def connect(url: str, dbname: str = None, autocommit: bool = False):
    """
    Create a connection to a Postgres database.

    :param url: the Postgres instance URL
    :param dbname: the target database name (if it differs from the one
        specified in the URL)
    :param autocommit: Set the `autocommit` flag on the connection?
    :return: a psycopg2 connection
    """
    # Parse the URL.  (We'll need the pieces to construct an ogr2ogr connection
    # string.)
    dbp: ParseResult = urlparse(url)
    # Create a dictionary to hold the arguments for the connection.  (We'll
    # unpack it later.)
    cnx_opt = {
        k: v for k, v in
        {
            'host': dbp.hostname,
            'port': int(dbp.port),
            'database': dbname if dbname is not None else dbp.path[1:],
            'user': dbp.username,
            'password': dbp.password
        }.items() if v is not None
    }
    cnx = psycopg2.connect(**cnx_opt)
    # If the caller requested that the 'autocommit' flag be set...
    if autocommit:
        # ...do that now.
        cnx.autocommit = True
    return cnx


def db_exists(url: str,
              dbname: str = None,
              admindb: str = 'postgres') -> bool:
    """
    Does a given database on a Postgres instance exist?

    :param url: the Postgres instance URL
    :param dbname: the name of the database to test
    :param admindb: the name of an existing (presumably the main) database
    :return: `True` if the database exists, otherwise `False`
    """
    # Let's see what we got for the database name.
    _dbname = dbname
    # If the caller didn't specify a database name...
    if not _dbname:
        # ...let's figure it out from the URL.
        db: ParseResult = urlparse(url)
        _dbname = db.path[1:]
    # Now, let's do this!
    with connect(url=url, dbname=admindb) as cnx:
        with cnx.cursor() as crs:
            # Execute the SQL query that counts the databases with a specified
            # name.
            crs.execute(
                sql_phrasebook.select_db_count.format(_dbname)
            )
            # If the count isn't zero (0) the database exists.
            return crs.fetchone()[0] != 0


def create_schema(url: str, schema: str):
    """
    Create a schema in the database.

    :param url: the URL of the database instance
    :param schema: the name of the schema
    """
    with connect(url=url) as cnx:
        with cnx.cursor() as crs:
            crs.execute(sql_phrasebook.create_schema.format(schema))


def schema_exists(url: str, schema: str):
    """
    Does a given schema exist within a Postgres database?

    :param url: the Postgres instance URL and database
    :param schema: the name of the schema
    :return: `True` if the schema exists, otherwise `False`
    """
    # If the database specified in the URL doesn't exist...
    if not db_exists(url=url):
        # ...it stands to reason that the schema cannot exist.
        return False
    # At this point, it looks as thought database exists, so let's check for
    # the schema.
    with connect(url=url) as cnx:
        with cnx.cursor() as crs:
            # Execute the SQL query that counts the schemas with a specified
            # name.
            crs.execute(
                sql_phrasebook.select_schema_count.format(schema)
            )
            # If the count isn't zero (0) the database exists.
            return crs.fetchone()[0] != 0


def select_schema_tables(url: str, schema: str) -> Iterable[str]:
    """
    Select the names of the tables within a given schema.

    :param url: the URL of the dat
    :param schema: the name of the schema
    """
    with connect(url=url) as cnx:
        with cnx.cursor() as crs:
            crs.execute(sql_phrasebook.select_schema_tables.format(schema))
            for row in crs:
                yield row[0]


def drop_schema(url: str, schema: str):
    """
    Drop a schema from the database.

    :param url: the URL of the database instance
    :param schema: the name of the schema
    """
    with connect(url=url, autocommit=True) as cnx:
        with cnx.cursor() as crs:
            # Execute the SQL query that counts the schemas with a specified
            # name.
            crs.execute(
                sql_phrasebook.drop_schema.format(schema)
            )


def create_db(
        url: str,
        dbname: str,
        admindb: str = 'postgres'):
    """
    Create a database on a Postgres instance.

    :param url: the Postgres instance URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    :return:
    """
    with connect(url=url, dbname=admindb) as cnx:
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with cnx.cursor() as crs:
            crs.execute(sql_phrasebook.create_db.format(dbname))


def create_extensions(url: str):
    """
    Create the necessary database extensions.

    :param url: the URL of the database instance
    """
    with connect(url=url, autocommit=True) as cnx:
        with cnx.cursor() as crs:
            # Make sure the extensions are installed.
            for sql in sql_phrasebook.create_extensions:
                crs.execute(sql)
