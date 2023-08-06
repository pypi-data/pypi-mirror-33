# -*- coding: utf-8 -*-

"""
takumi_sqlalchemy
~~~~~~~~~~~~~~~~~

Sqlachmey utilities for Takumi.

Settings:

    - DB_SETTINGS

        dict: {
          '<app_name>': {
            'dsn': {
              'master': '<dsn>',
              'slave': '<dsn>'
            },
            'pool_size': <pool_size>,
            'max_overflow': <max_overflow>,
            'pool_recycle': <pool_recycle>
          }
        }
"""

from .hook import patch_psycopg_hook
from .database import db


__all__ = ['patch_psycopg_hook', 'db']
