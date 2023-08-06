This package includes the Rockset Python SDK that includes the following:

- Native Python API to connect to Rockset, manage data and execute queries. This API includes Rockset's query builder that allows for programmatic construction of advanced queries using native Python expressions.

- `rock` command line utility to interact, manage and operate Rockset from a shell command line. `rock` CLI includes a SQL REPL command-line that can be entered using `rock sql`.

- SQL connector for Python, which conforms to the Python DB API 2.0 specification. Refer to https://www.python.org/dev/peps/pep-0249 for more details.

- SQLAlchemy dialect to bridge Rockset and SQLAlchemy applications. SQLAlchemy users can connect to Rockset using 'rockset://<api_key>:@<api_server>'

Rockset documentation is available at:
http://docs.rockset.com


Release Notes
-------------

.. Add a line for every user-facing feature change
.. rst syntax requires leaving an empty line before and after the sub-bullets

- 0.4.0-alpha.20180515+ecbe2a0

    - Moved to new /org/{org} REST API
    - Add SQL support that is accessible from `rock sql`
    - Field `_id` defines the unique identified for a document (`:id` deprecated)
    - Field `_meta` captures all other system generated fields in documents (`:collection` etc deprecated)

- 0.3.0-alpha.20180314+410b55e

    - Add py query builder support for <, <=, > and >= operators for string values

- v0.3.0-alpha.20180206+168be7d

    - Add ``F.collect()`` support to accumulate entire parent documents as part of a bucket aggregation

- v0.3.0-alpha.20171206+7debcb7

    - Add ``collect`` aggregate function to support bucket aggregations
    - Add support for ``F.count()`` to do equivalent of count(*)

- v0.3.0-alpha.20171121+d8c7961

    - Sensitive fields can now be masked or anonymized, when collections are created from AWS S3. See ``rock help create collection`` for more details.
    - AWS S3 bucket path prefixes can be provided to create a collection from only a subset of data in an AWS S3 bucket.
    - Support Parquet file format for loading data into collections.

- v0.3.0-alpha.20170919+49e62f5

    - Simpler REST API 0.3
    - Add fence API and write APIs returning commit markers
    - Add View creation progress indicator to describe view API
    - More user-friendly error messages and Python exception strings
    - Enforce and document various system-wide limits

- v0.2.2-alpha.20170824+dff8385

    - Support for next version of api_key and got rid of api_secrets
    - Added support for adding multiple documents in single API call
    - Added rockset.source to better support managing S3 sources while creating collections and collection sources while creating views.
    - Better client support for views with multiple analyzer mappings
    - py/client supports async_requests to have multiple concurrent queries pending
    - Support for sampling queries and queries on nested documents
    - Backend: better query optimization support

- v0.2.1-alpha.20170707+88ab952

    - Added support for views

- v0.2.1-alpha.20170629+4492c9a

    - py/client now respects HTTP_PROXY and HTTPS_PROXY ENV variables

- v0.2.1-alpha.20170629+7b050f5

    - Fix bug that made limit queries not composable

- v0.2.1-alpha.20170628+303f256

    - Added cursors with automatic pagination support
    - Added support for limit & skip queries

- v0.2.1-alpha.20170624+e6aee25

    - Added support for lookup operator for JOINs
    - Auth token auto refresh will support long lived Client() objects

- v0.2.1-alpha.20170615+f3df06e

    - Parallel aggregations for faster performance
    - Aggregation support for nested fields
    - Aggregation support over large data sets
    - Rewrote backend service discovery to make it elastic
    - User friendly messages for all py/client exceptions

- v0.1.1-alpha

    - First alpha release



