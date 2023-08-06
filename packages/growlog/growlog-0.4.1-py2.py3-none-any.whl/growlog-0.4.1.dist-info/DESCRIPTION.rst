========
Overview
========



A simple CLI garden journal

* Free software: MIT license

Installation
============

::

    pip install growlog


Quickstart
============
        $ growlog

        > No growlog found, creating a new one!

        What type of plant is this?:

        ...

You can also see the help menu:

        $ growlog --help 

        Usage: growlog [OPTIONS]

        Options:
          --add     Add a crop to your growlog
          --update  Update a crop in your growlog
          --remove  Remove a crop from your growlog
          --help    Show this message and exit.

Documentation
=============

https://growlog.readthedocs.io/

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

0.1.0 (2018-06-05)
------------------

* First release on PyPI.


