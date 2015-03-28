virtualenv-api - an API for virtualenv
======================================

[![Build Status](https://travis-ci.org/sjkingo/virtualenv-api.svg)](https://travis-ci.org/sjkingo/virtualenv-api)

[virtualenv](http://www.virtualenv.org/) is a tool to create isolated Python
environments.  Unfortunately, it does not expose a native Python API. This
package aims to provide an API in the form of a wrapper around virtualenv.

It can be used to create and delete environments and perform package management
inside the environment.

Full support is provided for Python 2.7 and Python 3.3+.

Installation
------------

The latest stable release is available on [PyPi](https://pypi.python.org/pypi/virtualenv-api):

```
$ pip install virtualenv-api
```

Please note that the distribution is named `virtualenv-api`, yet the Python package
is named `virtualenvapi`.

Alternatively, you may fetch the latest version from git:

```
$ pip install git+https://github.com/sjkingo/virtualenv-api.git
```

Examples
--------

* To begin managing an environment (it will be created if it does not exist):

```python
from virtualenvapi.manage import VirtualEnvironment
env = VirtualEnvironment('/path/to/environment/name')
```

You may also specify the Python interpreter to use in this environment by
passing the `python` argument to the class constructor (new in 2.1.3):

```python
env = VirtualEnvironment('/path/to/environment/name', python='python3')
```

* Check if the `mezzanine` package is installed:

```python
>>> env.is_installed('mezzanine')
False
```

* Install the latest version of the `mezzanine` package:

```python
>>> env.install('mezzanine')
```

* Install version 1.4 of the `django` package (this is pip's syntax):

```python
>>> env.install('django==1.4')
```

* Upgrade the `django` package to the latest version:

```python
>>> env.upgrade('django')
```

* Uninstall the `mezzanine` package:

```python
>>> env.uninstall('mezzanine')
```

Packages may be specified as name only (to work on the latest version),
using pip's package syntax (e.g. `django==1.4`) or as a tuple of `('name', 'ver')`
(e.g. `('django', '1.4')`).

* A package may be installed directly from a git repository (must end with `.git`):

```python
>>> env.install('git+git://github.com/sjkingo/cartridge-payments.git')
```

* Instances of the environment provide an `installed_packages` property:

```python
>>> env.installed_packages
[('django', '1.5'), ('wsgiref', '0.1.2')]
```

* A list of package names is also available in the same manner:

```python
>>> env.installed_package_names
['django', 'wsgiref']
```

* Search for a package on PyPI:

```python
>>> env.search('requests')[0]
('requests', 'Python HTTP for Humans.')
```

Verbose output from each command is available in the environment's `build.log`
file, which is appended to with each operation. Any errors are logged to `build.err`.
