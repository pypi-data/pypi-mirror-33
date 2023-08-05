========
Overview
========



Description
===========

I'm Cédric ROMAN.

``ngoschema`` aims at building classes based on a `JSON schema
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_.

User can declare its attributes in a schema (along with their type, default
value) and the class will be built with accessors to check and validate data.

User can add methods and override setters/getters, but the library provides a
boiler plate to automatically create the class, nicely instrumented (with loggers,
exception handling, type checking, data validation, etc...).

Objects created are come with managers to load/save them into files.

Serialization tools are provided that can be used to do code generation.

The library is build on top of `python-jsonschema-object
<https://github.com/cwacek/python-jsonschema-objects>`_, with a lot of hacking,
which allows to create classes
from a JSON-schema.

Both projects use the library `python-jsonchema
<http://python-jsonschema.readthedocs.io/en/latest/validate/>`_, a python
implementation for JSON schema validation.

* Free software: GNU General Public License v3

Installation
============

::

    pip install ngoschema

Documentation
=============

https://python-ngoschema.readthedocs.io/

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

0.1.0 (2018-06-04)
------------------

* First release on PyPI.


