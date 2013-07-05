__author__  = 'Bruce Kroeze'
__credits__ = ['James Addison', ]

from threading import local

_threadlocals = local()


def get_current_request():
    return get_thread_variable('request', None)


def set_thread_variable(key, var):
    setattr(_threadlocals, key, var)


def get_thread_variable(key, default=None):
    return getattr(_threadlocals, key, default)
