# -*- coding: utf-8 -*-


def normalize_dsn(dsn):
    if isinstance(dsn, str):
        return {'master': dsn, 'slave': dsn}
    return dsn
