import os
import subprocess
import six
import sys

from virtualenvapi.util import normalize_package, normalize_package_name, to_text, get_env_path, get_package_name
from virtualenvapi.exceptions import *


class VirtualEnvironment(object):

    def __init__(self, path=None, python=None, cache=None, readonly=False, system_site_packages=False):

        if path is None:
            path = get_env_path()

        if not path:
            raise VirtualenvPathNotFound('Path for virtualenv is not define or virtualenv is not activate')

        self.python = python
        self.system_site_packages = system_site_packages

        # remove trailing slash so os.path.split() behaves correctly
        if path[-1] == os.path.sep:
            path = path[:-1]

        # Expand path so shell shortcuts may be used such as ~
        self.path = os.path.abspath(os.path.expanduser(path))

        self.env = os.environ.copy()

        # Blacklist environment variables that will break pip in virtualenvs
        # See https://github.com/pypa/virtualenv/issues/845
        self.env.pop('__PYVENV_LAUNCHER__', None)

        if cache is not None:
            self.env['PIP_DOWNLOAD_CACHE'] = os.path.expanduser(os.path.expandvars(cache))

        self.readonly = readonly

        # True if the virtual environment has been set up through open_or_create()
        self._ready = False

    def __str__(self):
        return six.u(self.path)

    @property
    def _pip(self):
        """The arguments used to call pip."""

        # pip is called using the python interpreter to get around a long path
        # issue detailed in https://github.com/sjkingo/virtualenv-api/issues/30
        return [self._python_rpath, '-m', 'pip']

    @property
    def _python_rpath(self):
        """The relative path (from environment root) to python."""

        # Windows virtualenv installation installs pip to the [Ss]cripts
        # folder. Here's a simple check to support:
        if sys.platform == 'win32':
            return os.path.join('Scripts', 'python.exe')

        return os.path.join('bin', 'python')

    @property
    def pip_version(self):
        """Version of installed pip."""

        if not self._pip_exists:
            return None

        if not hasattr(self, '_pip_version'):
            # don't call `self._execute_pip` here as that method calls this one
            output = self._execute(self._pip + ['-V'], log=False).split()[1]
            self._pip_version = tuple([int(n) for n in output.split('.')])

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
        args = ['virtualenv']

        if self.system_site_packages:
            args.append('--system-site-packages')
        if self.python is None:
            args.append(self.name)
        else:
            args.extend(['-p', self.python, self.name])

        proc = subprocess.Popen(args, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = proc.communicate()
        returncode = proc.returncode
        if returncode:
            raise VirtualenvCreationException((returncode, output, self.name))

        self._write_to_log(output, truncate=True)
        self._write_to_error(error, truncate=True)

    def _execute_pip(self, args, log=True):
        """
        Executes pip commands.

        :param args: Arguments to pass to pip (list[str])
        :param log: Log the output to a file [default: True] (boolean)
        :return: See _execute
        """

        # Copy the pip calling arguments so they can be extended
        exec_args = list(self._pip)

        # Older versions of pip don't support the version check argument.
        # Fixes https://github.com/sjkingo/virtualenv-api/issues/35
        if self.pip_version[0] >= 6:
            exec_args.append('--disable-pip-version-check')

        exec_args.extend(args)
        return self._execute(exec_args, log=log)

    def _execute(self, args, log=True):
        """Executes the given command inside the environment and returns the output."""
        if not self._ready:
            self.open_or_create()
        output = ''
        error = ''
        try:
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
            raise OSError('%s: %s' % (prog, six.u(str(e))))
        except subprocess.CalledProcessError as e:
            output, error = e.output
            e.output = output
            raise e
        finally:
            if log:
                try:
                    self._write_to_log(output)
                    self._write_to_error(error)
                except NameError:
                    pass  # We tried

    def _write_to_log(self, s, truncate=False):
        """Writes the given output to the log file, appending unless `truncate` is True."""

        # if truncate is True, set write mode to truncate
        with open(self._logfile, 'w' if truncate else 'a') as fp:
            fp.writelines((to_text(s), ))

    def _write_to_error(self, s, truncate=False):
        """Writes the given output to the error file, appending unless `truncate` is True."""

        # if truncate is True, set write mode to truncate
        with open(self._errorfile, 'w' if truncate else 'a') as fp:
            fp.writelines((to_text(s)), )

    def _pip_exists(self):
        """Returns True if pip exists inside the virtual environment. Can be
        used as a naive way to verify that the environment is installed."""

        return os.path.isfile(os.path.join(self.path, 'bin', 'pip'))

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
        '-e .'
        '-r requirements.txt'

        If `force` is True, force an installation. If `upgrade` is True,
        attempt to upgrade the package in question. If both `force` and
        `upgrade` are True, reinstall the package and its dependencies.
        The `options` is a list of strings that can be used to pass to
        pip."""

        if self.readonly:
            raise VirtualenvReadonlyException()

        if options is None:
            options = []

        package_name = get_package_name(package)
        package_args = package_name.split() # '-e package_name' -> ['-e', 'package_name']

        package_name = normalize_package(package_name)

        if not (force or upgrade) and ('-r' in package_args and self.is_installed(package_name)):
            self._write_to_log('%s is already installed, skipping (use force=True to override)' % package_name)
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
            self._execute_pip(['install'] + package_args + options)
        except subprocess.CalledProcessError as e:
            raise PackageInstallationException((e.returncode, e.output, package_name))

    def uninstall(self, package):
        """Uninstalls the given package (given in pip's package syntax or a tuple of
        ('name', 'ver')) from this virtual environment."""

        package_name = normalize_package_name(get_package_name(package))

        if not self.is_installed(package_name):
            self._write_to_log('%s is not installed, skipping' % package_name)
            return
        try:
            self._execute_pip(['uninstall', '-y', package_name])
        except subprocess.CalledProcessError as e:
            raise PackageRemovalException((e.returncode, e.output, package_name))

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

        package_name = normalize_package_name(get_package_name(package))

        if not self.is_installed('wheel'):
            raise PackageWheelException((0, "Wheel package must be installed in the virtual environment", package_name))

        if not isinstance(options, list):
            raise ValueError("Options must be a list of strings.")

        try:
            self._execute_pip(['wheel', package_name] + options)
        except subprocess.CalledProcessError as e:
            raise PackageWheelException((e.returncode, e.output, package_name))

    def is_installed(self, package):
        """Returns True if the given package (given in pip's package syntax or a
        tuple of ('name', 'ver')) is installed in the virtual environment."""

        package = normalize_package(package)
        package_name, package_version = package

        package_name = package_name.lower()
        package_name_underscored = package_name.replace('-', '_').lower()

        if package_version is not None:
            for name, version in self.installed_packages:
                if name.lower() in [package_name, package_name_underscored] and version == package_version:
                    return True
        else:
            for name in self.installed_package_names:
                if name.lower() in [package_name, package_name_underscored]:
                    return True

        return False

    def upgrade(self, package, force=False):
        """Shortcut method to upgrade a package. If `force` is set to True,
        the package and all of its dependencies will be reinstalled, otherwise
        if the package is up to date, this command is a no-op."""

        self.install(package, upgrade=True, force=force)

    def upgrade_all(self):
        """
        Upgrades all installed packages to their latest versions.
        """

        for package_name in self.installed_package_names:
            self.install(package_name, upgrade=True)

    def search(self, term):
        """
        Searches the PyPi repository for the given `term` and returns a
        dictionary of results.

        New in 2.1.5: returns a dictionary instead of list of tuples
        """

        packages = {}
        results = self._execute_pip(['search', term], log=False)  # Don't want to log searches
        for result in results.split(os.linesep):
            try:
                name, description = result.split(six.u(' - '), 1)
            except ValueError:
                # '-' not in result so unable to split into tuple;
                # this could be from a multi-line description
                continue
            else:
                name = normalize_package(name)
                if not name:
                    continue
                packages[name] = description.split(six.u('<br'), 1)[0].strip()

        return packages

    def search_names(self, term):
        return list(self.search(term).keys())

    @property
    def installed_packages(self):
        """
        List of packages that are installed in this environment in
        the format [(name, ver), ..].
        """

        freeze_options = ['-l', '--all'] if self.pip_version >= (8, 1, 0) else ['-l']
        return list(map(normalize_package, filter(None, self._execute_pip(
                ['freeze'] + freeze_options).split(os.linesep))))

    @property
    def installed_package_names(self):
        """List of all package names that are installed in this environment."""

        return [name.lower() for name, _ in self.installed_packages]
