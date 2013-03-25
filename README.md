virtualenv-api - an API for virtualenv/pip
==========================================

This API can be used to programatically manage virtual environments such as deployed applications etc.

Sample usage (assuming environment does not yet exist):

```python
>>> env = VirtualEnvironment('/path/to/environment/name')
>>> env.is_installed('mezzanine')
False
>>> env.install('mezzanine')
>>> env.is_installed('mezzanine')
True
>>> env.install('django==1.5')
```
