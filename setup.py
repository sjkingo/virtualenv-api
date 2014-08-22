from setuptools import find_packages, setup


setup(
    name='virtualenv-api',
    version='2.0.0',
    license='BSD',
    author='Sam Kingston',
    author_email='sam@sjkwi.com.au',
    description='An API for virtualenv/pip',
    url='https://github.com/sjkingo/virtualenv-api',
    install_requires=['six', ],
    packages=find_packages(),
)
