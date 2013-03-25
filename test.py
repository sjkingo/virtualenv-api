#!/usr/bin/python

from virtualenv.manage import VirtualEnvironment

def sample_usage():
    env = VirtualEnvironment('/tmp/virtualenv.test')
    print 'mezzanine installed?', env.is_installed('mezzanine')
    env.install('mezzanine')
    print 'mezzanine installed?', env.is_installed('mezzanine')
    print 'django 1.5 installed?', env.is_installed('django==1.5')
    print env.installed_packages

    payments_repo = 'git+git://github.com/explodes/cartridge-payments.git'
    print 'cartridge-payments installed?', env.is_installed(payments_repo)
    env.install(payments_repo)
    print 'cartridge-payments installed?', env.is_installed(payments_repo)
    print env.installed_packages


if __name__ == '__main__':
    sample_usage()
