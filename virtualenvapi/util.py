import os
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


def get_env_path():
    prefix_name = 'real_prefix'
    virtual_env_path_environ_key = 'VIRTUAL_ENV'

    path = None

    real_prefix = (hasattr(sys, prefix_name) and getattr(sys, prefix_name)) or None
    if real_prefix:
        path = os.environ.get(virtual_env_path_environ_key)
        if not path:
            path = sys.prefix

    return path


def normalize_package(package):
    """Normalizes package name or tuple and returns a tuple (name, ver)."""

    if isinstance(package, tuple):
        return (normalize_package_name(to_text(package[0])), to_text(package[1]) if package[1] else None)

    return split_package_name(package)


def split_package_name(package):
    """Splits the given package name and returns a tuple (name, ver)."""

    parts = package.split(six.u('=='))
    if len(parts) == 1:
        return (normalize_package_name(to_text(parts[0])), None)
    else:
        return (normalize_package_name(to_text(parts[0])), to_text(parts[1]))


def normalize_package_name(name):
    """Fixes names of packages, like installed with -e option or downloaded from git"""

    # -e package_name -> package_name
    name = name.strip().split()[-1]

    if name.endswith(six.u('.git')):
        # git+https://github.com/me/package_name.git -> package_name
        return os.path.split(name)[1].partition('.git')[0]

    if six.u('#egg=') in name:
        # git+https://github.com/me/package_name.git@6e7d262c1d9ad5047ada8b8ad471f3f1852dad87#egg=new_name -> new_name
        return name.split(six.u('#egg='))[-1]

    if six.u('.git@') in name:
        # git+https://github.com/me/package_name.git@1.2.3 -> package_name
        return os.path.split(name)[1].partition('.git@')[0]

    return name


def get_package_name(package):
    if isinstance(package, tuple):
        if package[1] is None:
            return package[0]

        return '=='.join(package)

    return package
