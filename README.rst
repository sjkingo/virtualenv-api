virtualenv-api - an API for virtualenv
======================================

|Build Status|
|Latest version|
|BSD License|

`virtualenv`_ is a tool to create isolated Python environments. Unfortunately,
it does not expose a native Python API.  This package aims to provide an API in
the form of a wrapper around virtualenv.

It can be used to create and delete environments and perform package management
inside the environment.

Full support is provided for Python 2.7 and Python 3.3+.

.. _virtualenv: http://www.virtualenv.org/
.. |Build Status| image:: https://travis-ci.org/sjkingo/virtualenv-api.svg
   :target: https://travis-ci.org/sjkingo/virtualenv-api
.. |Latest version| image:: https://img.shields.io/pypi/v/virtualenv-api.svg
   :target: https://pypi.python.org/pypi/virtualenv-api
.. |BSD License| image:: https://img.shields.io/pypi/l/virtualenv-api.svg
   :target: https://github.com/sjkingo/virtualenv-api/blob/master/LICENSE


Installation
------------

The latest stable release is available on `PyPi`_:

::

    $ pip install virtualenv-api

Please note that the distribution is named ``virtualenv-api``, yet the Python
package is named ``virtualenvapi``.

Alternatively, you may fetch the latest version from git:

::

    $ pip install git+https://github.com/sjkingo/virtualenv-api.git

.. _PyPi: https://pypi.python.org/pypi/virtualenv-api

Examples
--------

-  To begin managing an environment (it will be created if it does not
   exist):

.. code:: python

    from virtualenvapi.manage import VirtualEnvironment
    env = VirtualEnvironment('/path/to/environment/name')

You may also specify the Python interpreter to use in this environment by
passing the ``python`` argument to the class constructor (new in 2.1.3):

.. code:: python

    env = VirtualEnvironment('/path/to/environment/name', python='python3')

If you have already activated a virtualenv and wish to operate on it, simply
call ``VirtualEnvironment`` with no arguments:

.. code:: python

    env = VirtualEnvironment()

*New in 2.1.7:*

An optional argument ``readonly`` may be provided (defaults to ``False``) that
will prevent all operations that could potentially modify the environment.

-  Check if the ``mezzanine`` package is installed:

.. code:: python

    >>> env.is_installed('mezzanine')
    False

-  Install the latest version of the ``mezzanine`` package:

.. code:: python

    >>> env.install('mezzanine')

-  A wheel of the latest version of the ``mezzanine`` package (new in
   2.1.4):

.. code:: python

    >>> env.wheel('mezzanine')

-  Install version 1.4 of the ``django`` package (this is pip’s syntax):

.. code:: python

    >>> env.install('django==1.4')

-  Upgrade the ``django`` package to the latest version:

.. code:: python

    >>> env.upgrade('django')

-  Upgrade all packages to their latest versions (new in 2.1.7):

.. code:: python

    >>> env.upgrade_all()

-  Uninstall the ``mezzanine`` package:

.. code:: python

    >>> env.uninstall('mezzanine')

Packages may be specified as name only (to work on the latest version), using
pip’s package syntax (e.g. ``django==1.4``) or as a tuple of ``('name',
'ver')`` (e.g. ``('django', '1.4')``).

-  A package may be installed directly from a git repository (must end
   with ``.git``):

.. code:: python

    >>> env.install('git+git://github.com/sjkingo/cartridge-payments.git')

*New in 2.1.10:*

-  A package can be installed in pip's *editable* mode by prefixing the package
   name with `-e` (this is pip's syntax):

.. code:: python

    >>> env.install('-e git+https://github.com/stephenmcd/cartridge.git')

-  Instances of the environment provide an ``installed_packages``
   property:

.. code:: python

    >>> env.installed_packages
    [('django', '1.5'), ('wsgiref', '0.1.2')]

-  A list of package names is also available in the same manner:

.. code:: python

    >>> env.installed_package_names
    ['django', 'wsgiref']

-  Search for a package on PyPI (changed in 2.1.5: this now returns a
   dictionary instead of list):

.. code:: python

    >>> env.search('virtualenv-api')
    {'virtualenv-api': 'An API for virtualenv/pip'}
    >>> len(env.search('requests'))
    231

-  The old functionality (pre 2.1.5) of ``env.search`` may be used:

.. code:: python

    >>> list(env.search('requests').items())
    [('virtualenv-api', 'An API for virtualenv/pip')]

Verbose output from each command is available in the environment’s
``build.log`` file, which is appended to with each operation. Any errors are
logged to ``build.err``.
