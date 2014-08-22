from os import environ
import six
import sys


def to_unicode(source):
    if six.PY3:
        if isinstance(source, str):
            return source
        else:
            return source.decode("utf-8")
    elif six.PY2:
        if isinstance(source, unicode):
            return source
        return source.decode("utf-8")
    else:
        return source


def get_env_path():
    prefix_name = 'real_prefix'
    virtual_env_path_environ_key = 'VIRTUAL_ENV'

    path = None

    real_prefix = (hasattr(sys, prefix_name) and getattr(sys, prefix_name)) or None
    if real_prefix:
        path = environ.get(virtual_env_path_environ_key)
        if not path:
            path = sys.prefix

    return path


def split_package_name(p):
    """Splits the given package name and returns a tuple (name, ver)."""
    s = p.split(six.u('=='))
    if len(s) == 1:
        return (to_unicode(s[0]), None)
    else:
        return (to_unicode(s[0]), to_unicode(s[1]))
