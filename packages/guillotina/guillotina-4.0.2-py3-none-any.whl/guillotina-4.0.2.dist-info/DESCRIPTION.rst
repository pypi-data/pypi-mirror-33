Introduction
============

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
   :target: http://guillotina.readthedocs.io/en/latest/

.. image:: https://travis-ci.org/plone/guillotina.svg?branch=master
   :target: https://travis-ci.org/plone/guillotina

.. image:: https://codecov.io/gh/plone/guillotina/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/plone/guillotina/branch/master
   :alt: Test Coverage

.. image:: https://img.shields.io/pypi/pyversions/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina/
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina

.. image:: https://img.shields.io/pypi/l/guillotina.svg
   :target: https://pypi.python.org/pypi/guillotina/
   :alt: License

.. image:: https://badges.gitter.im/plone/guillotina.png
   :target: https://gitter.im/plone/guillotina
   :alt: Chat

Please `read the detailed docs <http://guillotina.readthedocs.io/en/latest/>`_


This is the working project of the next generation Guillotina server based on asyncio.


Dependencies
------------

* python >= 3.6
* postgresql >= 9.6


Quickstart
----------

We use pip::

  pip install guillotina


Run postgresql
--------------

If you don't have a postgresql server to play with, you can run one easily
with docker.

Download and start the docker container by running::

  make run-postgres



Run the server
--------------

To run the server::

    g


Then...

    curl http://localhost:8080


Or, better yet, use postman to start playing with API.


Getting started with development
--------------------------------

Using pip::

  ./bin/pip install requirements.txt
  ./bin/pip install -e .[test]


Run tests
---------

We're using pytest::

    ./bin/pytest guillotina

and for test coverage::

    ./bin/pytest --cov=guillotina guillotina/

With file watcher...

    ./bin/ptw guillotina --runner=./bin/py.test


To run tests with cockroach db::

   USE_COCKROACH=true ./bin/pytest guillotina

Default
-------

Default root access can be done with AUTHORIZATION header : Basic root:root


Docker
------

You can also run Guillotina with Docker!


First, run postgresql::

    docker run --rm \
        -e POSTGRES_DB=guillotina \
        -e POSTGRES_USER=guillotina \
        -p 127.0.0.1:5432:5432 \
        --name postgres \
        postgres:9.6

Then, run guillotina::

    docker run --rm -it \
        --link=postgres -p 127.0.0.1:8080:8080 \
        guillotina/guillotina:latest \
        g -c '{"databases": [{"db": {"storage": "postgresql", "dsn": "postgres://guillotina:@postgres/guillotina"}}], "root_user": {"password": "root"}}'


This assumes you have a config.yaml in your current working directory


Chat
----

Join us to talk about Guillotina at https://gitter.im/plone/guillotina


4.0.2 (2018-06-22)
------------------

- Support for extra values on Field properties
  [bloodbare]

- Don't fail on read-only pg

- Fix nested schema null value deserialization error
  [vangheem]

- Fix use of AllowSingle with children overriding the same permission
  [bloodbare]


4.0.1 (2018-06-07)
------------------

- Implement minimal passing mypy compatibility
  [vangheem]

- Rename `BaseObject.__annotations__` to `BaseObject.__gannotations__` to prevent
  namespace clashes with mypy and other things
  [vangheem]


4.0.0 (2018-06-05)
------------------

- `guillotina.browser.Response` moved to `guillotina.response.Response`
- move `guillotina.browser.ErrorResponse` to `guillotina.response.ErrorResponse`
- `guillotina.browser.UnauthorizedResponse` removed
- `guillotina.response.Response` no longer supports wrapping aiohttp responses
- `guillotina.response.Response` can now be raised as an exception
- returned or raised aiohttp responses now bypass guillotina renderer framework
- raising any Response as an exception aborts current transaction
- remove `IFrameFormatsJson`
- remove `IRenderFormats`, `IRendered` is now a named adapter lookup
- remove `app_settings.renderers` setting. Use the lookups
- remove `IDownloadView`
- remove `TraversableDownloadService`
- remove `IForbiddenAttribute`
- remove `ISerializableException`
- remove `IForbidden`
- by default, provide an async queue utility
- move `guillotina.files.CloudFileField` to `guillotina.fields.CloudFileField`
- fix deserialization with BucketListField
- fix required field of PatchField


3.3.12 (2018-05-30)
-------------------

- Reindex security of group object even if we aren't going to reindex it's children
  [vangheem]

- Refactor indexing so we can index security, provide `guillotina.catalog.index.index_object` function
  [vangheem]


3.3.11 (2018-05-30)
-------------------

- Move TRASHED annotation objects check to application logic instead
  of the query. This helps performance and query planer issue for cockroach
  [vangheem]


3.3.10 (2018-05-29)
-------------------

- Handle missing root object for database
  [vangheem]


3.3.9 (2018-05-29)
------------------

- Fix cache key format
  [vangheem]


3.3.8 (2018-05-29)
------------------

- Add more utilities: `execute`, `safe_unidecode`, `run_async`, `get_object_by_oid`
  [vangheem]

- Prevent db cache poisening between containers of dynamic databases
  [vangheem]

- Do not reuse transaction objects with get_containers
  [vangheem]


3.3.7 (2018-05-23)
------------------

- async pool should commit when using transaction
  [vangheem]


3.3.6 (2018-05-23)
------------------

- async pool should execute futures of request
  [vangheem]


3.3.5 (2018-05-22)
------------------

- specify `acl` field name for access_users and access_roles indexer
  so we can easily reindex security
  [vangheem]


- prevent running the same indexer multiple times
  [vangheem]

- be able to manually index object by using
  `guillotina.catalog.index.add_object(ob, modified=True, payload={})`
  [vangheem]

- Fix bug in CORS with tus when guillotina was on different domain than
  web application calling it
  [vangheem]


3.3.4 (2018-05-21)
------------------

- Make sure we write to a non-shared txn when creating db object
  [vangheem]


3.3.3 (2018-05-21)
------------------

- Use exists instead of get_names for dynamic dbs
  [vangheem]

3.3.2 (2018-05-20)
------------------

- Cockroachdb supports cascade and jsonb now
  [vangheem]


3.3.1 (2018-05-19)
------------------

- only return task on request.execute_futures if there are futures
  to run
  [vangheem]


3.3.0 (2018-05-19)
------------------

- Change reindexing security to futures, not queue for more
  consistent performance
  [vangheem]

- Remove IBeforeObjectAssignedEvent as it wasn't used
  [vangheem]

- Rename `directives.index` to `directives.index_field`
  [vangheem]

- Be able to specify priority on `@configure.subscriber`. Lower
  is higher priority.
  [vangheem]

- Indexer now sends full object for ICatalogUtility.remove
  instead of tuple of data
  [vangheem]


3.2.7 (2018-05-15)
------------------

- Indexing gathers all data on update instead of
  overwriting indexed data
  [vangheem]


3.2.6 (2018-05-12)
------------------

- Provide IDatabaseManager.exists for dummy db impelementation
  [vangheem]


3.2.5 (2018-05-12)
------------------

- add IDatabaseManager.exists method to be able to check if db exists
  [vangheem]

...

You are seeing a truncated changelog.

You can read the `changelog file <https://github.com/plone/guillotina/blob/master/CHANGELOG.rst>`_
for a complete list.



