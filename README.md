virtualenv-api - an API for virtualenv/pip
==========================================

This API can be used to programatically manage [virtual environments](http://www.virtualenv.org/en/latest/#what-it-does).
Instantiating the `VirtualEnvironment` class with a path will either create the
environment if it does not exist, or manage an existing environment.

Sample usage (assuming environment does not yet exist):

```python
>>> from virtualenv.api import VirtualEnvironment
>>> env = VirtualEnvironment('/path/to/environment/name')
>>> env.is_installed('mezzanine')
False
>>> env.install('mezzanine')
>>> env.is_installed('mezzanine')
True
>>> env.install('django==1.4')
>>> env.upgrade('django')
```

The above code has created a new virtual environment and installed `mezzanine`
and `django` into it. The API can transparently work with both new and existing
environments, like so (assuming above code is run first):

```python
>>> from virtualenv.api import VirtualEnvironment
>>> env = VirtualEnvironment('/path/to/environment/name')
>>> env.is_installed('mezzanine')
True
>>> env.is_installed('django')
True
```
