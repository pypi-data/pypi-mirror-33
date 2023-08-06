# -*- coding: utf-8 -*-

import random
from sqlalchemy.orm import Session


# ref: http://techspot.zzzeek.org/2012/01/11/django-style-database-routers-in-sqlalchemy/  # noqa
class RoutingSession(Session):
    """Routing session based on binding name
    """
    def __init__(self, engines, *args, **kwargs):
        super(RoutingSession, self).__init__(*args, **kwargs)
        self._name = None
        self.engines = engines
        self.slaves = [e for r, e in engines.items() if r != 'master']
        if not self.slaves:
            self.slaves = engines

    def get_bind(self, mapper=None, clause=None):
        if self._name:
            return self.engines[self._name]
        elif self._flushing:
            return self.engines['master']
        else:
            return random.choice(self.slaves)

    def using_bind(self, name):
        self._name = name
        return self
