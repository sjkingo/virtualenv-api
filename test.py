#!/usr/bin/python

from virtualenv.manage import VirtualEnvironment

def sample_usage():
    env = VirtualEnvironment('/tmp/virtualenv.test')
    print env.is_installed('mezzanine')
    env.install('mezzanine')
    print env.is_installed('mezzanine')
    print env.is_installed('django')


if __name__ == '__main__':
    sample_usage()
