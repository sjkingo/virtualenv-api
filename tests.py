import os
import random
import shutil
import string
import sys
import tempfile
import unittest

from virtualenvapi import __version__, __file__ as virtualenvapi_file_path
from virtualenvapi.manage import VirtualEnvironment

virtualenvapi_module_path = os.path.dirname(os.path.dirname(virtualenvapi_file_path))
packages_for_tests = ['pep8']
non_lowercase_packages_for_test = ['Pillow']
git_packages_for_test = ['git+https://github.com/pytest-dev/pytest.git@6.2.3']
all_packages_for_tests = packages_for_tests + non_lowercase_packages_for_test + git_packages_for_test

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class TestBase(unittest.TestCase):
    """
    Base class for test cases to inherit from.
    """

    env_path = None

    def setUp(self):
        self.env_path = tempfile.mkdtemp()
        self.virtual_env_obj = VirtualEnvironment(self.env_path)

    def tearDown(self):
        if os.path.exists(self.env_path):
            shutil.rmtree(self.env_path)

    def _install_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.install(pack)

    def _uninstall_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.uninstall(pack)


class InstalledTestCase(TestBase):
    """
    Test install/uninstall operations.
    """

    def test_installed(self):
        self.assertFalse(self.virtual_env_obj.is_installed(''.join(random.sample(string.ascii_letters, 30))))

    def test_install(self):
        for pack in all_packages_for_tests:
            self.virtual_env_obj.install(pack)
            self.assertTrue(self.virtual_env_obj.is_installed(pack))

    def test_install_requirements(self):
        """test installing Python packages from a pip requirements file"""

        # create a temporary requirements.txt file with some packages
        with tempfile.NamedTemporaryFile('w') as tmp_requirements_file:
            tmp_requirements_file.write('\n'.join(packages_for_tests))
            tmp_requirements_file.flush()

            self.virtual_env_obj.install('-r {}'.format(tmp_requirements_file.name))
            for pack in packages_for_tests:
                self.assertTrue(self.virtual_env_obj.is_installed(pack))

    def test_install_editable(self):
        self.virtual_env_obj.install('-e git+file://{}#egg=virtualenv-api'.format(virtualenvapi_module_path))
        print(self.virtual_env_obj.installed_packages)
        self.assertTrue(self.virtual_env_obj.is_installed('virtualenv-api'))
        self.assertFalse(self.virtual_env_obj.is_installed(('virtualenv-api', __version__)))

    def test_uninstall(self):
        self._install_packages(all_packages_for_tests)
        for pack in all_packages_for_tests:
            self.virtual_env_obj.uninstall(pack)
            self.assertFalse(self.virtual_env_obj.is_installed(pack))

    def test_uninstall_editable(self):
        self.virtual_env_obj.install('-e git+file://{}#egg=virtualenv-api'.format(virtualenvapi_module_path))
        self.assertFalse(self.virtual_env_obj.is_installed('virtualenv-api'))
        self.assertFalse(self.virtual_env_obj.is_installed(('virtualenv-api', __version__)))

    def test_wheel(self):
        self.virtual_env_obj.install('wheel') # required for this test
        for pack in packages_for_tests:
            self.virtual_env_obj.wheel(pack, options=['--wheel-dir=/tmp/wheelhouse'])
            self.virtual_env_obj.install(pack, options=['--no-index', '--find-links=/tmp/wheelhouse'])
            self.assertTrue(self.virtual_env_obj.is_installed(pack))


class SearchTestCase(TestBase):
    """
    Test pip search.
    """

    def test_search(self):
        for pack in all_packages_for_tests:
            result = self.virtual_env_obj.search(pack)
            self.assertIsInstance(result, dict)
            self.assertTrue(bool(result))
            if result:
                self.assertIn(pack.lower(), [k.split(' (')[0].lower() for k in result.keys()])

    def test_search_names(self):
        for pack in all_packages_for_tests:
            result = self.virtual_env_obj.search_names(pack)
            self.assertIsInstance(result, list)
            self.assertIn(pack.lower(), [k.split(' (')[0].lower() for k in result])


class PythonArgumentTestCase(TestBase):
    """
    Test passing a different interpreter path to `VirtualEnvironment` (`virtualenv -p`).
    """

    def setUp(self):
        self.env_path = tempfile.mkdtemp()
        self.python = which('python')
        self.assertIsNotNone(self.python)
        self.virtual_env_obj = VirtualEnvironment(self.env_path, python=self.python)

    def test_python_version(self):
        self.assertEqual(self.virtual_env_obj.python, self.python)
        self.assertEqual(
            os.path.dirname(self.python),
            os.path.dirname(which('pip'))
        )


class SystemSitePackagesTest(unittest.TestCase):
    """
    test coverage for using system-site-packages flag

    This verifies the presence of the no-global-site-packages
    file in the venv for non-system packages venv and
    verified it is not present for the true case

    """
    def setUp(self):
        """
        snapshot system package list
        """
        self.dir = tempfile.mkdtemp()
        self.no_global = (
            "lib/python{}.{}"
            "/no-global-site-packages.txt"
        ).format(
            sys.version_info.major,
            sys.version_info.minor
        )

    def tearDown(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)

    def test_system_site_packages(self):
        """
        test that creating a venv with system_site_packages=True
        results in a venv that does not contain the no-global-site-packages file

        """
        venv = VirtualEnvironment(self.dir, system_site_packages=True)
        venv._create()
        expected = os.path.join(venv.path, self.no_global)
        self.assertTrue(
            not os.path.exists(expected)
        )

    def test_no_system_site_packages(self):
        """
        test that creating a venv with system_site_packages=False
        results in a venv that contains the no-global-site-packages
        file

        """
        venv = VirtualEnvironment(self.dir)
        venv._create()
        expected = os.path.join(venv.path, self.no_global)
        self.assertTrue(
            os.path.exists(expected)
        )


if __name__ == '__main__':
    unittest.main()
