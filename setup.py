from setuptools import find_packages, setup

from virtualenvapi import __version__

setup(
    name='virtualenv-api',
    version=__version__,
    license='BSD',
    author='Sam Kingston and AUTHORS',
    author_email='sam@sjkwi.com.au',
    description='An API for virtualenv/pip',
    long_description=open('README.rst', 'r').read(),
    url='https://github.com/sjkingo/virtualenv-api',
    install_requires=['six',
                      'virtualenv'
                      ],
    packages=find_packages(),
)
