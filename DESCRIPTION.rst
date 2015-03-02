fredapi: Python API for FRED (Federal Reserve Economic Data)
============================================================

``fredapi`` is a Python API for the
`FRED <http://research.stlouisfed.org/fred2/>`__ data provided by the
Federal Reserve Bank of St. Louis. ``fredapi`` provides a wrapper in
python to the `FRED web
service <http://api.stlouisfed.org/docs/fred/>`__, and also provides
several conveninent methods for parsing and analyzing point-in-time data
(i.e. historic data revisions) from
`ALFRED <http://research.stlouisfed.org/tips/alfred/>`__

``fredapi`` makes use of ``pandas`` and returns data to you in a
``pandas`` ``Series`` or ``DataFrame``

Installation
------------

.. code:: sh

    pip install fredapi

Basic Usage
-----------

First you need an API key, you can `apply for
one <http://api.stlouisfed.org/api_key.html>`__ for free on the FRED
website. Once you have your API key, you can set it in one of three
ways:

-  set it to the evironment variable FRED\_API\_KEY
-  save it to a file and use the 'api\_key\_file' parameter
-  pass it directly as the 'api\_key' parameter

.. code:: python

    from fredapi import Fred
    fred = Fred(api_key='insert api key here')
    data = fred.get_series('SP500')

Working with data revisions
---------------------------

Many economic data series contain frequent revisions. ``fredapi``
provides several convenient methods for handling data revisions and
answering the quesion of what-data-was-known-when.

In `ALFRED <http://research.stlouisfed.org/tips/alfred/>`__ there is the
concept of a *vintage* date. Basically every *observation* can have
three dates associated with it: *date*, *realtime\_start* and
*realtime\_end*.

-  date: the date the value is for
-  realtime\_start: the first date the value is valid
-  realitime\_end: the last date the value is valid

For instance, there has been three observations (data points) for the
GDP of 2014 Q1:

.. code:: xml

    <observation realtime_start="2014-04-30" realtime_end="2014-05-28" date="2014-01-01" value="17149.6"/>
    <observation realtime_start="2014-05-29" realtime_end="2014-06-24" date="2014-01-01" value="17101.3"/>
    <observation realtime_start="2014-06-25" realtime_end="2014-07-29" date="2014-01-01" value="17016.0"/>

This means the GDP value for Q1 2014 has been released three times.
First release was on 4/30/2014 for a value of 17149.6, and then there
have been two revisions on 5/29/2014 and 6/25/2014 for revised values of
17101.3 and 17016.0, respectively.

Get first data release only (i.e. ignore revisions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    data = fred.get_series_first_release('GDP')

Get latest data
~~~~~~~~~~~~~~~

Note that this is the same as simply calling ``get_series()``

.. code:: python

    data = fred.get_series_latest_release('GDP')

Get latest data known on a given date
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fred.get_series_as_of_date('GDP', '6/1/2014')

Get all data release dates
~~~~~~~~~~~~~~~~~~~~~~~~~~

This returns a ``DataFrame`` with all the data from ALFRED

.. code:: python

    df = fred.get_series_all_releases('GDP')
    df.tail()

Get all vintage dates
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    vintage_dates = fred.get_series_vintage_dates('GDP')

Search for data series
~~~~~~~~~~~~~~~~~~~~~~

You can always search for data series on the FRED website. But sometimes
it can be more convenient to search programmatically. ``fredapi``
provides a ``search()`` method that does a fulltext search and returns a
``DataFrame`` of results.

.. code:: python

    fred.search('potential gdp')

You can also search by release id and category id with various options

.. code:: python

    df1 = fred.search_by_release(11)
    df2 = fred.search_by_category(101, limit=10, order_by='popularity', sort_order='desc')

Dependencies
------------

-  `pandas <http://pandas.pydata.org/>`__

More Examples
-------------

- I have a `blog post with more examples <http://mortada.net/python-api-for-fred.html>`__ written in an `IPython` notebook
