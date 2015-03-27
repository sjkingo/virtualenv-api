from os import environ
import six
import sys


def to_text(source):
    if six.PY3:
        if isinstance(source, str):
            return source
        else:
            return source.decode("utf-8")
    elif six.PY2:
        if isinstance(source, unicode):
            return source.encode("utf-8")
        return source
    else:
        return source


def to_ascii(source):
    if isinstance(source, six.string_types):
        return "".join([c for c in source if ord(c) < 128])


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
        return (to_text(s[0]), None)
    else:
        return (to_text(s[0]), to_text(s[1]))
