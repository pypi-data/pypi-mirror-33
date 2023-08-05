.. role:: python(code)
    :language: python


================
encrypted-config
================

.. image:: https://img.shields.io/pypi/v/encrypted-config.svg
    :target: https://pypi.org/project/encrypted-config
    :alt: package version from PyPI

.. image:: https://travis-ci.com/mbdevpl/encrypted-config.svg?branch=master
    :target: https://travis-ci.com/mbdevpl/encrypted-config
    :alt: build status from Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/mbdevpl/encrypted-config?svg=true
    :target: https://ci.appveyor.com/project/mbdevpl/encrypted-config
    :alt: build status from AppVeyor

.. image:: https://codecov.io/gh/mbdevpl/encrypted-config/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/encrypted-config
    :alt: test coverage from Codecov

.. image:: https://img.shields.io/pypi/l/encrypted-config.svg
    :target: https://github.com/mbdevpl/encrypted-config/blob/master/NOTICE
    :alt: license

Library and command-line tool for reading and writing of partially encrypted configuration files.

.. contents::
    :backlinks: none


How to use
==========

.. code:: python

    import encrypted_config


How to NOT use
==============

Running this library on an system to which anyone else has access is not secure.

If anyone else can access your private key, they can also decrypt the configuration.


Algorithms
==========

The library relies on RSA.


Requirements
============

Python version 3.4 or later.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.

Tested on Linux, OS X and Windows.
