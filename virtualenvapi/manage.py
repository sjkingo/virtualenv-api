from os import linesep, environ
import os.path
import subprocess
import six
import sys

from virtualenvapi.util import split_package_name, to_text, get_env_path, to_ascii
from virtualenvapi.exceptions import *


class VirtualEnvironment(object):

    def __init__(self, path=None, python=None, cache=None, readonly=False):

        if path is None:
            path = get_env_path()

        if not path:
            raise VirtualenvPathNotFound('Path for virtualenv is not define or virtualenv is not activate')

        self.python = python

        # remove trailing slash so os.path.split() behaves correctly
        if path[-1] == os.path.sep:
            path = path[:-1]

        # Expand path so shell shortcuts may be used such as ~
        self.path = os.path.abspath(os.path.expanduser(path))

        self.env = environ.copy()
        if cache is not None:
            self.env['PIP_DOWNLOAD_CACHE'] = os.path.expanduser(os.path.expandvars(cache))

        self.readonly = readonly

        # True if the virtual environment has been set up through open_or_create()
        self._ready = False

    def __str__(self):
        return six.u(self.path)

    @property
    def _pip_rpath(self):
        """The relative path (from environment root) to pip."""
        # Windows virtualenv installation installs pip to the [Ss]cripts
        # folder. Here's a simple check to support:
        if sys.platform == 'win32':
            return os.path.join('Scripts', 'pip.exe')
        return os.path.join('bin', 'pip')

    @property
    def pip_version(self):
        """Version of installed pip."""
        if not self._pip_exists:
            return None
        if not hasattr(self, '_pip_version'):
            string_version = self._execute([self._pip_rpath, '-V']).split()[1]
            self._pip_version = tuple([int(n) for n in string_version.split('.')])
        return self._pip_version

    @property
    def root(self):
        """The root directory that this virtual environment exists in."""
        return os.path.split(self.path)[0]

    @property
    def name(self):
        """The name of this virtual environment (taken from its path)."""
        return os.path.basename(self.path)

    @property
    def _logfile(self):
        """Absolute path of the log file for recording installation output."""
        return os.path.join(self.path, 'build.log')

    @property
    def _errorfile(self):
        """Absolute path of the log file for recording installation errors."""
        return os.path.join(self.path, 'build.err')

    def _create(self):
        """Executes `virtualenv` to create a new environment."""
        if self.readonly:
            raise VirtualenvReadonlyException()
        if self.python is None:
            args = ['virtualenv', self.name]
        else:
            args = ['virtualenv', '-p', self.python, self.name]
        proc = subprocess.Popen(args, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        returncode = proc.returncode
        if returncode:
            raise VirtualenvCreationException((returncode, output, self.name))
        self._write_to_log(output, truncate=True)
        self._write_to_error(error, truncate=True)

    def _execute(self, args, log=True):
        """Executes the given command inside the environment and returns the output."""
        if not self._ready:
            self.open_or_create()
        output = ''
        error = ''
        try:
            if args[0] == 'pip':
                args += ['--disable-pip-version-check']
            proc = subprocess.Popen(args, cwd=self.path, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            returncode = proc.returncode
            if returncode:
                raise subprocess.CalledProcessError(returncode, proc, (output, error))
            return to_text(output)
        except OSError as e:
            # raise a more meaningful error with the program name
            prog = args[0]
            if prog[0] != os.sep:
                prog = os.path.join(self.path, prog)
            raise OSError('%s: %s' % (prog, six.u(e.message)))
        except subprocess.CalledProcessError as e:
            output, error = e.output
            e.output = output
            raise e
        finally:
            if log:
                try:
                    self._write_to_log(to_text(output))
                    self._write_to_error(to_text(error))
                except NameError:
                    pass  # We tried

    def _write_to_log(self, s, truncate=False):
        """Writes the given output to the log file, appending unless `truncate` is True."""
        # if truncate is True, set write mode to truncate
        with open(self._logfile, 'w' if truncate else 'a') as fp:
            fp.writelines((to_text(s) if six.PY2 else to_text(s), ))

    def _write_to_error(self, s, truncate=False):
        """Writes the given output to the error file, appending unless `truncate` is True."""
        # if truncate is True, set write mode to truncate
        with open(self._errorfile, 'w' if truncate else 'a') as fp:
            fp.writelines((to_text(s)), )

    def _pip_exists(self):
        """Returns True if pip exists inside the virtual environment. Can be
        used as a naive way to verify that the environment is installed."""
        return os.path.isfile(os.path.join(self.path, self._pip_rpath))

    def open_or_create(self):
        """Attempts to open the virtual environment or creates it if it
        doesn't exist.
        XXX this should probably be expanded to do some proper checking?"""
        if not self._pip_exists():
            self._create()
        self._ready = True

    def install(self, package, force=False, upgrade=False, options=None):
        """Installs the given package into this virtual environment, as
        specified in pip's package syntax or a tuple of ('name', 'ver'),
        only if it is not already installed. Some valid examples:

         'Django'
         'Django==1.5'
         ('Django', '1.5')

        If `force` is True, force an installation. If `upgrade` is True,
        attempt to upgrade the package in question. If both `force` and
        `upgrade` are True, reinstall the package and its dependencies.
        The `options` is a list of strings that can be used to pass to
        pip."""
        if self.readonly:
            raise VirtualenvReadonlyException()
        if options is None:
            options = []
        if isinstance(package, tuple):
            package = '=='.join(package)
        if package.startswith('-e'):
            package_args = package.split()
        else:
            package_args = [package]
        if not (force or upgrade) and self.is_installed(package_args[-1]):
            self._write_to_log('%s is already installed, skipping (use force=True to override)' % package_args[-1])
            return
        if not isinstance(options, list):
            raise ValueError("Options must be a list of strings.")
        if upgrade:
            options += ['--upgrade']
            if force:
                options += ['--force-reinstall']
        elif force:
            options += ['--ignore-installed']
        try:
            self._execute([self._pip_rpath, 'install'] + package_args + options)
        except subprocess.CalledProcessError as e:
            raise PackageInstallationException((e.returncode, e.output, package))

    def uninstall(self, package):
        """Uninstalls the given package (given in pip's package syntax or a tuple of
        ('name', 'ver')) from this virtual environment."""
        if isinstance(package, tuple):
            package = '=='.join(package)
        if not self.is_installed(package):
            self._write_to_log('%s is not installed, skipping' % package)
            return
        try:
            self._execute([self._pip_rpath, 'uninstall', '-y', package])
        except subprocess.CalledProcessError as e:
            raise PackageRemovalException((e.returncode, e.output, package))

    def wheel(self, package, options=None):
        """Creates a wheel of the given package from this virtual environment, 
        as specified in pip's package syntax or a tuple of ('name', 'ver'),
        only if it is not already installed. Some valid examples:

         'Django'
         'Django==1.5'
         ('Django', '1.5')

        The `options` is a list of strings that can be used to pass to
        pip."""
        if self.readonly:
            raise VirtualenvReadonlyException()
        if options is None:
            options = []
        if isinstance(package, tuple):
            package = '=='.join(package)
        if not self.is_installed('wheel'):
            raise PackageWheelException((0, "Wheel package must be installed in the virtual environment", package))
        if not isinstance(options, list):
            raise ValueError("Options must be a list of strings.")
        try:
            self._execute([self._pip_rpath, 'wheel', package] + options)
        except subprocess.CalledProcessError as e:
            raise PackageWheelException((e.returncode, e.output, package))

    def is_installed(self, package):
        """Returns True if the given package (given in pip's package syntax or a
        tuple of ('name', 'ver')) is installed in the virtual environment."""
        if isinstance(package, tuple):
            package = '=='.join(package)
        if package.endswith('.git'):
            pkg_name = os.path.split(package)[1][:-4]
            return pkg_name in self.installed_package_names or \
                    pkg_name.replace('_', '-') in self.installed_package_names
        pkg_tuple = split_package_name(package)
        if pkg_tuple[1] is not None:
            return pkg_tuple in self.installed_packages
        else:
            return pkg_tuple[0] in self.installed_package_names

    def upgrade(self, package, force=False):
        """Shortcut method to upgrade a package. If `force` is set to True,
        the package and all of its dependencies will be reinstalled, otherwise
        if the package is up to date, this command is a no-op."""
        self.install(package, upgrade=True, force=force)

    def upgrade_all(self):
        """
        Upgrades all installed packages to their latest versions.
        """
        for pkg in self.installed_package_names:
            self.install(pkg, upgrade=True)

    def search(self, term):
        """
        Searches the PyPi repository for the given `term` and returns a
        dictionary of results.

        New in 2.1.5: returns a dictionary instead of list of tuples
        """
        packages = {}
        results = self._execute([self._pip_rpath, 'search', term], log=False)  # Don't want to log searches
        for result in results.split(linesep):
            try:
                name, description = result.split(six.u(' - '), 1)
            except ValueError:
                # '-' not in result so unable to split into tuple;
                # this could be from a multi-line description
                continue
            else:
                name = name.strip()
                if len(name) == 0:
                    continue
                packages[name] = description.split(six.u('<br'), 1)[0].strip()
        return packages

    def search_names(self, term):
        return list(self.search(term).keys())

    @property
    def installed_packages(self):
        """
        List of all packages that are installed in this environment in
        the format [(name, ver), ..].
        """
        freeze_options = ['-l', '--all'] if self.pip_version >= (8, 1, 0) else ['-l']
        return list(map(split_package_name, filter(None, self._execute(
                [self._pip_rpath, 'freeze'] + freeze_options).split(linesep))))

    @property
    def installed_package_names(self):
        """List of all package names that are installed in this environment."""
        return [name.lower() for name, _ in self.installed_packages]
