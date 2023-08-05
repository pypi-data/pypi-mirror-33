========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-ngoci/badge/?style=flat
    :target: https://readthedocs.org/projects/python-ngoci
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/numengo/python-ngoci.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/numengo/python-ngoci

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/numengo/python-ngoci?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/numengo/python-ngoci

.. |requires| image:: https://requires.io/github/numengo/python-ngoci/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/numengo/python-ngoci/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/numengo/python-ngoci/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/numengo/python-ngoci

.. |version| image:: https://img.shields.io/pypi/v/ngoci.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ngoci

.. |commits-since| image:: https://img.shields.io/github/commits-since/numengo/python-ngoci/v0.1.2.svg
    :alt: Commits since latest release
    :target: https://github.com/numengo/python-ngoci/compare/v0.1.2...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/ngoci.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/ngoci

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ngoci.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/ngoci

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ngoci.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/ngoci


.. end-badges

Utilities for continuous integration, development workflow, and package management

* Free software: GNU General Public License v3

Installation
============

::

    pip install ngoci

Documentation
=============

https://python-ngoci.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
