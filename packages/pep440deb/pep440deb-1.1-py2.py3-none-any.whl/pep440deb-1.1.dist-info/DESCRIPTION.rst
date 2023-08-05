======================================================
 ``pep440deb`` -- Map PEP440 version to Debian policy
======================================================

Debian and Python has two distincts conventions for version scheme. Each have a
different way to tell a pre-release tag, etc. ``pep440deb`` is a little helper
for managing translation of Python package version to Debian version policy.

::

    $ pep440deb 1.0a1
    1.0~a1
    $ pep440deb --echo --pypi pip
    9.0.1 9.0.1
    $ echo 1.0.dev0 | pep440deb --file -
    1.0~dev0

You can use it from Python::

    >>> from pep440deb import debianize
    >>> debianize('1.0a1')
    '1.0~a1'


Installation
============

Install it from PyPI::

    pip install pep440deb


