from setuptools import find_packages, setup


setup(
    name='virtualenv-api',
    version='2.1.7',
    license='BSD',
    author='Sam Kingston and AUTHORS',
    author_email='sam@sjkwi.com.au',
    description='An API for virtualenv/pip',
    long_description_markdown_filename='README.md',
    url='https://github.com/sjkingo/virtualenv-api',
    setup_requires=['setuptools-markdown'],
    install_requires=['six'],
    packages=find_packages(),
)
