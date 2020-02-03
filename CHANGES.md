# Changes

## 2.1.18 - 2020-02-03

* #46: Blacklist env var in subprocess calls to fix bug in MacOS/Homebrew installs (@irvinlim)
* Change build versions to match supported Python versions (@sjkingo)

## 2.1.17 - 2018-11-15

* #40: Fix for test cases failing (@irvinlim)
* #39: Fix for `is_installed` not handling capitilized names properly (@irvinlim)
* Support Python 3.7 (@sjkingo)

## 2.1.16 - 2017-03-17

* Fix bug in test script where temporary directories were not being removed (@sjkingo)
* #35: Don't pass unsupported argument to old versions of pip (@sjkingo)
* Always call pip through the Python interpreter to avoid a too-long shebang error (@sjkingo)
* #26: Fix incorrect subclassing of base test class that was causing extreme test durations (@sjkingo)

## 2.1.15 - 2017-03-17

* #34: Add support for `pip -r` requirements files (@jzafran and @sjkingo)

## 2.1.14 - 2017-02-22

* #33: Add support for `system-site-packages` option (@evansde77)

## 2.1.13 - 2016-10-26

* #31: Workaround to prevent shebang length errors when calling pip (@rmb938)

## 2.1.12 - 2016-10-22

* #29: Fix AttributeError when raising OSError from inside environment (@rmb938)

## 2.1.11 - 2016-07-14

* #28: Add support for locating pip on win32 (@eoghancunneen)

## 2.1.10 - 2016-06-03

* #27: Support installing an editable package (`-e`) (@sjkingo)

## 2.1.9 - 2016-05-01

* Move version number to library instead of `setup.py` (@sjkingo)
* Support Python 3.5 (@sjkingo)
* #24: Fixed failing test suite by adding missing dependency (@mcyprian)

## 2.1.8 - 2016-04-01

* #21: Converted `README.md` to an rST document to remove dependency on
  `setuptools-markdown` (@sjkingo)

## 2.1.7 - 2015-08-10

* Added `upgrade_all()` function to upgrade all packages in an environment (@sjkingo)
* Added `readonly` argument to constructing environment that can be used to prevent
  operations that could potentially modify the environment (@sjkingo)
* Added support for passing ~ to construct environment (e.g. `~user/venv`) (@sjkingo)

## 2.1.6 - 2015-06-10

 * Version bump for broken PyPi release (@sjkingo)
   (no new changes to code)

## 2.1.5 - 2015-06-10

 * Improved search function that will return more accurate results. This
   includes a breaking change where the package list returned by `env.search()`
   is now a dictionary. (@sjkingo)
 * Prevent pip from checking for new version of itself and polluting the output
   of some commands (@sjkingo)

## 2.1.4 - 2015-06-04

 * Support for creating a wheel of packages (@rmb938)

## 2.1.3 - 2015-03-28

 * Support changing the interpreter path (@jlafon)
 * Improve Unicode support in pip search that broke tests (@jlafon)

## 2.1.2 - 2014-11-25

 * Added test builds through Travis CI (@sjkingo)
 * Fixed default `options` bug introduced in 2.0.1 (@ColMcp, @sposs)
 * Updated example.py (@sjkingo)
 * Fix typo in logging (@yannik-ammann)

## 2.1.1 - 2014-11-19

 * Fix typo that broke from 2.1.0 release (@sjkingo)

## 2.1.0 - 2014-11-19

 * Python 3 support (@r1s)
 * Unit tests for base functionality (@r1s)
 * Better Unicode handling (@r1s)
 * Tuple support for specifying package versions (@philippeowagner)

## 2.0.1 - 2014-11-14

 * Support passing command line options directly to pip (@sposs)
 * Misc. PEP8 fixes (@sposs)

## 2.0.0 - 2014-04-09

 * Added pip search functionality
 * Re-worked underlying pip processing and error handling

## 1.0.0 - 2013-03-27

 * Initial release with basic install/uninstall
