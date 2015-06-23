#!/usr/bin/env python
import tempfile

from virtualenvapi.manage import VirtualEnvironment


def example(path=tempfile.mkdtemp('virtualenv.test')):
    print('Env path', path)
    env = VirtualEnvironment(path)

    print('django 1.5 installed?', env.is_installed('django==1.5'))

    print('mezzanine installed?', env.is_installed('mezzanine'))
    env.install('mezzanine')
    print('mezzanine installed?', env.is_installed('mezzanine'))

    print(env.installed_packages)

    repo = 'git+git://github.com/sjkingo/django_auth_ldap3.git'
    pkg = repo.split('/')[-1].replace('.git', '')
    print('django_auth_ldap3 installed?', env.is_installed(pkg))
    env.install(repo)
    print('django_auth_ldap3 installed?', env.is_installed(pkg))
    print(env.installed_packages)

    env.uninstall('mezzanine')
    print('mezzanine installed?', env.is_installed('mezzanine'))
    print(env.installed_packages)

    pkgs = env.search('requests')
    print('search for \'requests\':')
    print(len(pkgs), 'found:')
    print(pkgs)


if __name__ == '__main__':
    example()
