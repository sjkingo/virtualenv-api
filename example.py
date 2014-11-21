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

    payments_repo = 'git+git://github.com/sjkingo/cartridge-payments.git'
    payments_pkg = payments_repo.split('/')[-1].replace('.git', '')
    print('cartridge-payments installed?', env.is_installed(payments_pkg))
    env.install(payments_repo)
    print('cartridge-payments installed?', env.is_installed(payments_pkg))
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
