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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
