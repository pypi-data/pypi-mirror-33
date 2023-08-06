# -*- coding: utf-8 -*-

"""
takumi_sqlalchemy.hook
~~~~~~~~~~~~~~~~~~~~~~

Database related hook definition.

Hook definition:

    - after_load    Patch psycopg2 for gevent
"""

import itertools
from sqlalchemy.engine.url import make_url
from takumi import define_hook
from takumi_config import config

from .utils import normalize_dsn


@define_hook(event='after_load')
def patch_psycopg_hook():
    settings = config.settings['DB_SETTINGS']
    dsn = itertools.chain(*[normalize_dsn(v['dsn']).values()
                            for v in settings.values()])
    for d in dsn:
        schema = make_url(d)
        driver = schema.get_driver_name()
        if driver == 'psycopg2':
            break
    else:
        return

    # patch psycopg2
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
