import os
import random
import shutil
import string
import tempfile
from unittest import TestCase
import unittest
import sys
import six
from virtualenvapi.manage import VirtualEnvironment


packages_for_tests = ['pep8', 'wheel']


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

class TestBase(TestCase):
    env_path = None

    def setup_env(self):
        env_path = self.env_path
        if env_path is None:
            env_path = tempfile.mkdtemp('test_env')
            virt_env = VirtualEnvironment(env_path)
            virt_env._create()

        return env_path

    def setUp(self):
        self.env_path = self.setup_env()
        self.virtual_env_obj = VirtualEnvironment(self.env_path)

    def tearDown(self):
        if os.path.exists(self.env_path) and self.__class__.env_path is None:
            shutil.rmtree(self.env_path)

    def _install_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.install(pack)

    def _uninstall_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.uninstall(pack)


class InstalledTestCase(TestBase):

    def test_installed(self):
        self.assertFalse(self.virtual_env_obj.is_installed(''.join(random.sample(string.ascii_letters, 30))))

    def test_install(self):
        self._uninstall_packages(packages_for_tests)
        for pack in packages_for_tests:
            self.virtual_env_obj.install(pack)
            self.assertTrue(self.virtual_env_obj.is_installed(pack))

    def test_install_requirements(self):
        """test installing Python packages from a pip requirements file"""
        self._uninstall_packages(packages_for_tests)

        # create a temporary requirements.txt file with some packages
        with tempfile.NamedTemporaryFile('w') as tmp_requirements_file:
            tmp_requirements_file.write('\n'.join(packages_for_tests))
            tmp_requirements_file.flush()

            self.virtual_env_obj.install('-r {}'.format(tmp_requirements_file.name))
            for pack in packages_for_tests:
                self.assertTrue(self.virtual_env_obj.is_installed(pack))

    def test_uninstall(self):
        self._install_packages(packages_for_tests)
        for pack in packages_for_tests:
            if pack.endswith('.git'):
                pack = pack.split('/')[-1].replace('.git', '')
            self.virtual_env_obj.uninstall(pack)
            self.assertFalse(self.virtual_env_obj.is_installed(pack))

    def test_wheel(self):
        for pack in packages_for_tests:
            self.virtual_env_obj.wheel(pack, options=['--wheel-dir=/tmp/wheelhouse'])
            self.virtual_env_obj.install(pack, options=['--no-index', '--find-links=/tmp/wheelhouse', '--use-wheel'])
            self.assertTrue(self.virtual_env_obj.is_installed(pack))


class SearchTestCase(TestBase):

    def test_search(self):
        pack = packages_for_tests[0].lower()
        result = self.virtual_env_obj.search(pack)
        self.assertIsInstance(result, dict)
        self.assertTrue(bool(result))
        if result:
            self.assertIn(pack, [k.split(' (')[0].lower() for k in result.keys()])

    def test_search_names(self):
        pack = packages_for_tests[0].lower()
        result = self.virtual_env_obj.search_names(pack)
        self.assertIsInstance(result, list)
        self.assertIn(pack, [k.split(' (')[0].lower() for k in result])


class Python3TestCase(TestBase):

    def setUp(self):
        self.env_path = self.setup_env()
        self.python = which('python')
        self.assertIsNotNone(self.python)
        self.virtual_env_obj = VirtualEnvironment(self.env_path, python=self.python)

    def test_python_version(self):
        self.assertEqual(self.virtual_env_obj.python, self.python)
        self.assertEqual(
            os.path.dirname(self.python),
            os.path.dirname(which('pip'))
        )


class LongPathTestCase(TestBase):

    def setup_env(self):
        env_path = self.env_path
        if env_path is None:
            # See: https://github.com/pypa/pip/issues/1773 This test may not be 100% accurate, tips on improving?
            # Windows and OSX have their own limits so this may not work 100% of the time
            long_path = "".join([random.choice(string.digits) for _ in range(0, 129)])
            env_path = tempfile.mkdtemp('test_long_env-'+long_path)
            virt_env = VirtualEnvironment(env_path)
            virt_env._create()

        return env_path

    def test_pip_error(self):
        self.assertRaises(OSError, self.virtual_env_obj._execute_pip, ['-V'], raw_pip=True)
        try:
            self.virtual_env_obj._execute_pip(['-V'])
        except OSError:
            self.fail("_execute_pip raised OSError unexpectedly")


class EnvironmentTest(TestBase):

    def setup_env(self):
        act_filename = 'activate_this.py'
        env_path = super(EnvironmentTest, self).setup_env()
        act_path = os.path.join(env_path, 'bin', act_filename)
        if six.PY2:
            execfile(act_path, dict(__file__=act_path))
        elif six.PY3:
            with open(act_path, "r") as fh:
                exec(fh.read())
        else:
            raise EnvironmentError('Unknown version of python')
        return env_path


class SystemSitePackagesTest(TestCase):
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
    # ToDo refactoring
    if len(sys.argv) == 2 and sys.argv[1].startswith('--env='):
        env_path = sys.argv[1].split('=', 1)[-1]
        BaseTest.env_path = env_path
        sys.argv = sys.argv[:1]

    unittest.main()
