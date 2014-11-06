from os import linesep, environ
import os.path
import subprocess

from virtualenvapi.util import split_package_name
from virtualenvapi.exceptions import VirtualenvCreationException, PackageInstallationException, PackageRemovalException


class VirtualEnvironment(object):
    # True if the virtual environment has been set up through open_or_create()
    _ready = False

    def __init__(self, path, cache=None):
        # remove trailing slash so os.path.split() behaves correctly
        if path[-1] == '/':
            path = path[:-1]
        self.path = path
        self.env = environ.copy()
        if cache is not None:
            self.env['PIP_DOWNLOAD_CACHE'] = os.path.expanduser(os.path.expandvars(cache))

    def __str__(self):
        return self.path

    @property
    def _pip_rpath(self):
        """The relative path (from environment root) to pip."""
        return os.path.join('bin', 'pip')

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
        proc = subprocess.Popen(['virtualenv', self.name], cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        try:
            proc = subprocess.Popen(args, cwd=self.path, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
            returncode = proc.returncode
            if returncode:
                raise subprocess.CalledProcessError(returncode, proc, (output, error))
            return output
        except OSError as e:
            # raise a more meaningful error with the program name
            prog = args[0]
            if prog[0] != os.sep:
                prog = os.path.join(self.path, prog)
            raise OSError('%s: %s' % (prog, str(e)))
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
            fp.write(s + linesep)

    def _write_to_error(self, s, truncate=False):
        """Writes the given output to the error file, appending unless `truncate` is True."""
        # if truncate is True, set write mode to truncate
        with open(self._errorfile, 'w' if truncate else 'a') as fp:
            fp.write(s + linesep)

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

    def install(self, package, force=False, upgrade=False, options=[]):
        """Installs the given package (given in pip's package syntax) 
        into this virtual environment only if it is not already installed.
        If `force` is True, force an installation. If `upgrade` is True,
        attempt to upgrade the package in question. If both `force` and
        `upgrade` are True, reinstall the package and its dependencies.
        The `options` is a list of strings that can be used to pass to
        pip."""
        if not (force or upgrade) and self.is_installed(package):
            self._write_to_log('%s is already installed, skipping (use force=True to override)' % package)
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
            self._execute([self._pip_rpath, 'install', package] + options)
        except subprocess.CalledProcessError as e:
            raise PackageInstallationException((e.returncode, e.output, package))

    def uninstall(self, package):
        """Uninstalls the given package (given in pip's package syntax) from
        this virtual environment."""
        if not self.is_installed(package):
            self._write_to_log('%s is not installed, skipping')
            return
        try:
            self._execute([self._pip_rpath, 'uninstall', '-y', package])
        except subprocess.CalledProcessError as e:
            raise PackageRemovalException((e.returncode, e.output, package))

    def is_installed(self, package):
        """Returns True if the given package (given in pip's package syntax)
        is installed in the virtual environment."""
        if package.endswith('.git'):
            pkg_name = os.path.split(package)[1][:-4]
            return pkg_name in self.installed_package_names
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

    def search(self, term):
        packages = []
        results = self._execute([self._pip_rpath, 'search', term], log=False)  # Don't want to log searches
        for result in results.split('\n'):
            try:
                name, description = result.split(' - ', 1)
                packages.append((name.strip(), description.strip()))
            except ValueError:
                name, description = packages[-1]
                packages[-1] = (name, description + ' ' + result.strip())
        return packages

    def search_names(self, term):
        return [name for name, description in self.search(term)]

    @property
    def installed_packages(self):
        """List of all packages that are installed in this environment."""
        pkgs = []  #: [(name, ver), ..]
        l = self._execute([self._pip_rpath, 'freeze', '-l']).split(linesep)
        for p in l:
            if p == '':
                continue
            pkgs.append(split_package_name(p))
        return pkgs

    @property
    def installed_package_names(self):
        """List of all package names that are installed in this environment."""
        return [name.lower() for name, _ in self.installed_packages]
