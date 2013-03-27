from setuptools import setup

URL = 'https://github.com/sjkingo/virtualenv-api'

setup(
    name='virtualenv-api',
    version='1.0.0',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    packages=['virtualenv'],
    license='BSD',
    url=URL,
    description='An API for virtualenv.',
    long_description='Please see %s/blob/master/README.md for more information and examples.' % URL,
    install_requires=[
        'virtualenv >= 1.9',
        'pip >= 1.3',
    ],
)
