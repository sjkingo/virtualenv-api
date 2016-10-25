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


packages_for_pre_install = ['pep8', 'wheel']
packages_for_tests = ['flask', 'git+git://github.com/sjkingo/django_auth_ldap3.git']


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


class BaseTest(TestCase):

    env_path = None

    def setUp(self):
        self.env_path = self.setup_env()
        self.virtual_env_obj = VirtualEnvironment(self.env_path)

    def setup_env(self):
        env_path = self.env_path
        if env_path is None:
            env_path = tempfile.mkdtemp('test_env')
            virt_env = VirtualEnvironment(env_path)
            virt_env._create()
            for pack in packages_for_pre_install:
                virt_env.install(pack)

        return env_path

    def _install_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.install(pack)

    def _uninstall_packages(self, packages):
        for pack in packages:
            self.virtual_env_obj.uninstall(pack)

    def test_installed(self):
        for pack in packages_for_pre_install:
            self.assertTrue(self.virtual_env_obj.is_installed(pack))
        self.assertFalse(self.virtual_env_obj.is_installed(''.join(random.sample(string.ascii_letters, 30))))

    def test_install(self):
        self._uninstall_packages(packages_for_tests)
        for pack in packages_for_tests:
            self.virtual_env_obj.install(pack)
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

    def tearDown(self):
        if os.path.exists(self.env_path) and self.__class__.env_path is None:
            shutil.rmtree(self.env_path)


class Python3TestCase(BaseTest):

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


class LongPathTestCase(BaseTest):

    def setUp(self):
        self.env_path = self.setup_env()
        self.virtual_env_obj = VirtualEnvironment(self.env_path)

    def setup_env(self):
        env_path = self.env_path
        if env_path is None:
            # See: https://github.com/pypa/pip/issues/1773 This test may not be 100% accurate, tips on improving?
            # Windows and OSX have their own limits so this may not work 100% of the time
            long_path = "".join([random.choice(string.digits) for _ in range(0, 129)])
            env_path = tempfile.mkdtemp('test_long_env-'+long_path)
            virt_env = VirtualEnvironment(env_path)
            virt_env._create()
            for pack in packages_for_pre_install:
                virt_env.install(pack)

        return env_path

    def test_pip_error(self):
        self.assertRaises(OSError, self.virtual_env_obj._execute_pip, ['-V'], raw_pip=True)
        try:
            self.virtual_env_obj._execute_pip(['-V'])
        except OSError:
            self.fail("_execute_pip raised OSError unexpectedly")


class EnvironmentTest(BaseTest):

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


if __name__ == '__main__':
    # ToDo refactoring
    if len(sys.argv) == 2 and sys.argv[1].startswith('--env='):
        env_path = sys.argv[1].split('=', 1)[-1]
        BaseTest.env_path = env_path
        sys.argv = sys.argv[:1]

    unittest.main()
