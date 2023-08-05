========
Overview
========



Library to facilitate chunked access of large ndarray-like volumes

* Free software: MIT license

Installation
============

::

    pip install chunkblocks

Documentation
=============

https://chunkblocks.readthedocs.io/

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

0.1.0 (2018-06-18)
------------------

* First release on PyPI.


