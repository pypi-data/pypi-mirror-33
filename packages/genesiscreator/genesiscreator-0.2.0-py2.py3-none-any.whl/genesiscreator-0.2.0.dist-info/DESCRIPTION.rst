========
Overview
========



A Crypto-Currency Genesis Block Creator

* Free software: BSD 3-Clause License

Installation
============

::

    pip install genesiscreator

Documentation
=============

https://python-genesiscreator.readthedocs.io/

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


Changelog
=========

0.1.0 (2018-07-01)
------------------

* First release on PyPI.


