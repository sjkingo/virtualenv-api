import os

from setuptools import find_packages, setup

from virtualenvapi import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r') as fh:
    long_description = fh.read()

with open(os.path.join(here,'requirements.txt'), 'r') as fh:
    requirements = fh.read().split("\n")

setup(
    name='virtualenv-api',
    version=__version__,
    license='BSD',
    author='Sam Kingston and AUTHORS',
    author_email='sam@sjkwi.com.au',
    description='An API for virtualenv/pip',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url='https://github.com/sjkingo/virtualenv-api',
    install_requires=requirements,
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
)
