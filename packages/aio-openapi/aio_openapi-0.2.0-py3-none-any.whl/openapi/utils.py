import os
import logging
from inspect import isclass


LOCAL = 'local'
DEV = 'dev'
PRODUCTION = 'production'
NO_DEBUG = {'0', 'false', 'no'}


def get_env():
    return os.environ.get('PYTHON_ENV') or PRODUCTION


def get_debug_flag():
    val = os.environ.get('DEBUG')
    if not val:
        return get_env() == LOCAL
    return val.lower() not in NO_DEBUG


def compact(**kwargs):
    return {k: v for k, v in kwargs.items() if v}


def compact_dict(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


def iter_items(data):
    items = getattr(data, 'items', None)
    if hasattr(items, '__call__'):
        return items()
    return iter(data)


def getLogger():
    level = (os.environ.get('LOG_LEVEL') or 'info').upper()
    if level != 'NONE':
        name = os.environ.get('APP_NAME') or 'openapi'
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))
        logger.addHandler(logging.StreamHandler())
        return logger


def is_subclass(value, Klass):
    return isclass(value) and issubclass(value, Klass)
