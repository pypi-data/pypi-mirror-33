Changelog
*********

0.1b1
=====

:Date: 2018-06-19

Changes
-------
* Support old `Python 2.7`, `Python 3.4`
* Config file name extension changed from ``".yaml"`` to ``".yml"``
* Default config file environment variable name
* Default config file path if no environment variable

Adds
----
* Some simple test cases
* CircleCI
* Codacy

0.1a3
=====
The first ever-usable version.

:Date: 2018-04-18

Changes
-------
* Now Python 3.5+ ONLY, because ``glob.iglob`` has no ``recursive`` argument and ``"**"`` wildcard in lower Python version

Bug Fixes
---------
* Backup directory errors
* OSS exception
