.. fredapi documentation master file, created by
   sphinx-quickstart on Fri Nov 12 15:00:52 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://img.shields.io/pypi/v/fredapi.svg
   :target: https://pypi.org/project/fredapi/
.. image:: https://img.shields.io/badge/License-Apache_2.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
|

Welcome to fredapi's documentation!
====================================

:code:`fredapi` is a Python API for the `FRED <http://research.stlouisfed.org/fred2/>`_ data provided by the
Federal Reserve Bank of St. Louis. :code:`fredapi` provides a wrapper in python to the
`FRED web service <http://api.stlouisfed.org/docs/fred/>`_, and also provides several convenient methods
for parsing and analyzing point-in-time data (i.e. historic data revisions) from `ALFRED <http://research.stlouisfed.org/tips/alfred/>`_

:code:`fredapi` makes use of :code:`pandas` and returns data to you in a :code:`pandas` :code:`Series` or :code:`DataFrame`.

For examples of how to use :code:`fredapi` please see the links below.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Quick Start <example_notebooks/00_quickstart.ipynb>
   Working With Data Revisions <example_notebooks/01_working_with_date_revisions.ipynb>
   Search for Data Series <example_notebooks/02_search_examples.ipynb>

.. toctree::
   :maxdepth: 1
   :caption: References

   Contribution Guide <references/contributing.md>
   API <references/api>
   Changelog <references/CHANGELOG.md>
   License <references/license>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
