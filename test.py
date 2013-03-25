#!/usr/bin/python

from virtualenv.manage import VirtualEnvironment

def sample_usage():
    env = VirtualEnvironment('/tmp/virtualenv.test')
    print 'mezzanine installed?', env.is_installed('mezzanine')
    env.install('mezzanine')
    print 'mezzanine installed?', env.is_installed('mezzanine')
    print 'django installed?', env.is_installed('django')


if __name__ == '__main__':
    sample_usage()
