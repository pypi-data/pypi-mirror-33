"""Integration between SQLAlchemy and Rockset.

Some code based on:
https://github.com/zzzeek/sqlalchemy/blob/rel_0_5/lib/sqlalchemy/databases/sqlite.py
which is released under the MIT license.

https://github.com/dropbox/PyHive
released under Apache License, Version 2.0

TODO
- fix and test get_schema_names
- fix and test _get_table_columns

"""

from __future__ import absolute_import
from __future__ import unicode_literals

from sqlalchemy import exc
from sqlalchemy import types
from sqlalchemy import util
from sqlalchemy.engine import default
from sqlalchemy.sql import compiler
from rockset.sql import dbapi

class _EverythingSet(object):
    """set contains *everything*"""
    def __contains__(self, _):
        return True

class RocksetIdentifierPreparer(compiler.IdentifierPreparer):
    # Just quote everything to make things simpler / easier to upgrade
    reserved_words = _EverythingSet()

_type_map = {
    # TODO : fix Python inferred types
    'bool': types.Boolean,
    'float': types.Float,
    'int': types.Integer,
    'str': types.String,
    'dict': types.JSON,
    'list': types.ARRAY,

    # types returned by the backend
    'bigint': types.BigInteger,
    'varchar': types.String,
    'document': types.JSON,
    'array': types.ARRAY,
}


class RocksetCompiler(compiler.SQLCompiler):
    def visit_char_length_func(self, fn, **kw):
        return 'length{}'.format(self.function_argspec(fn, **kw))


class RocksetTypeCompiler(compiler.GenericTypeCompiler):
    def visit_TEXT(self, type_, **kw):
        if type_.length:
            return 'VARCHAR({:d})'.format(type_.length)
        else:
            return 'VARCHAR'


class RocksetDialect(default.DefaultDialect):
    name = 'rockset'
    driver = 'rest'

    preparer = RocksetIdentifierPreparer
    statement_compiler = compiler.SQLCompiler
    type_compiler = compiler.GenericTypeCompiler

    supports_alter = False
    supports_pk_autoincrement = False
    supports_default_values = False
    supports_empty_insert = False
    supports_unicode_statements = True
    supports_unicode_binds = True
    returns_unicode_strings = True
    description_encoding = None
    supports_native_boolean = True

    @classmethod
    def dbapi(cls):
        return dbapi

    def create_connect_args(self, url):
        kwargs = {
            'api_server': '{}:{}'.format(url.host, url.port or 443),
            'api_key': url.username,
        }
        return ([], kwargs)

    def get_schema_names(self, connection, **kw):
        return [row['Schema'] for row in connection.execute('SHOW SCHEMAS')]

    def _get_table_columns(self, connection, table_name, schema):
        full_table = self.identifier_preparer.quote_identifier(table_name)
        if schema:
            full_table = (self.identifier_preparer.quote_identifier(schema)
                + '.' + full_table)
        try:
            return connection.execute('SHOW COLUMNS FROM {}'.format(full_table))
        except (dbapi.DatabaseError, exc.DatabaseError) as e:
            # Catch exceptions when fetching cursor's description
            # Check if table exists
            msg = hasattr(e, 'message') and e.message or None
            code = hasattr(e, 'code') and e.code or 0
            if 'does not exist' in msg or code == 404:
                raise exc.NoSuchTableError(table_name)
            else:
                raise

    def has_table(self, connection, table_name, schema=None):
        try:
            self._get_table_columns(connection, table_name, schema)
            return True
        except exc.NoSuchTableError:
            return False

    def get_columns(self, connection, table_name, schema=None, **kw):
        rows = self._get_table_columns(connection, table_name, schema)
        result = []
        for row in rows:
            try:
                coltype = _type_map[row['Type']]
            except KeyError:
                util.warn("Did not recognize type '%s' of column '%s'" % (
                    row['Type'], row['Column']))
                coltype = types.NullType
            result.append({
                'name': row['Column'],
                'type': coltype,
                # newer Rockset no longer includes this column
                'nullable': getattr(row, 'Null', True),
                'default': None,
            })
        return result

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        # no support for foreign keys.
        return []

    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        # no support for primary keys.
        return {'constrained_columns': ['_id'], 'name': None}

    def get_indexes(self, connection, table_name, schema=None, **kw):
        # no need for primary keys.
        return []

    def get_table_names(self, connection, schema=None, **kw):
        query = 'SHOW TABLES'
        if schema:
            query += (' FROM '
                + self.identifier_preparer.quote_identifier(schema))
        return [row['Table'] for row in connection.execute(query)]

    def do_rollback(self, dbapi_connection):
        # No transactions in Rockset
        pass

    def _check_unicode_returns(self, connection, additional_tests=None):
        # requests gives back Unicode strings
        return True

    def _check_unicode_description(self, connection):
        # requests gives back Unicode strings
        return True
