takumi-sqlalchemy
=================
.. image:: https://travis-ci.org/elemepi/takumi-sqlalchemy.svg?branch=master
    :target: https://travis-ci.org/elemepi/takumi-sqlalchemy

Sqlachmey utilities for Takumi.


Add Settings
------------

The setting ``DB_SETTINGS`` must be defined in *settings* module.

.. code:: python

    DB_SETTINGS = {
        'test_db': {'dsn': 'sqlite:///:memory:'}
    }


Init App
--------

It's not required to init app before using db. But it's recommended to init app
first:

.. code:: python

    db.init_app(app)


Query Database
--------------

The object ``db`` should be used to query database. And the only preferred way
to query database is to use the context manager:

.. code:: python

    with db['test_db'] as session:
        session.query(User).all()

    # or to use a different binding
    with db['test_db'].using_bind('master') as s:
        s.query(User).all()

    # or to tag the query
    with db['test_db'].tag(hello=123, world=90) as s:
        s.query(User).all()


