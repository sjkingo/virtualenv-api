Changes
=======

* Added support for passing ~ to construct environment (e.g. `~user/venv`)

2.1.6 - 2015-06-10

 * Version bump for broken PyPi release (@sjkingo)
   (no new changes to code)

2.1.5 - 2015-06-10

 * Improved search function that will return more accurate results. This
   includes a breaking change where the package list returned by `env.search()`
   is now a dictionary. (@sjkingo)
 * Prevent pip from checking for new version of itself and polluting the output
   of some commands (@sjkingo)

2.1.4 - 2015-06-04

 * Support for creating a wheel of packages (@rmb938)

2.1.3 - 2015-03-28

 * Support changing the interpreter path (@jlafon)
 * Improve Unicode support in pip search that broke tests (@jlafon)

2.1.2 - 2014-11-25

 * Added test builds through Travis CI (@sjkingo)
 * Fixed default `options` bug introduced in 2.0.1 (@ColMcp, @sposs)
 * Updated example.py (@sjkingo)
 * Fix typo in logging (@yannik-ammann)

2.1.1 - 2014-11-19

 * Fix typo that broke from 2.1.0 release (@sjkingo)

2.1.0 - 2014-11-19

 * Python 3 support (@r1s)
 * Unit tests for base functionality (@r1s)
 * Better Unicode handling (@r1s)
 * Tuple support for specifying package versions (@philippeowagner)

2.0.1 - 2014-11-14

 * Support passing command line options directly to pip (@sposs)
 * Misc. PEP8 fixes (@sposs)

2.0.0 - 2014-04-09

 * Added pip search functionality
 * Re-worked underlying pip processing and error handling

1.0.0 - 2013-03-27

 * Initial release with basic install/uninstall
