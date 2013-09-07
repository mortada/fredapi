# fredapi: Python API for FRED (Federal Reserve Economic Data)

## What is it

`fredapi` is a Python API for the [FRED](http://research.stlouisfed.org/fred2/) data provided by the
Federal Reserve Bank of St. Louis. `fredapi` provides a wrapper in python to the 
[FRED web service](http://api.stlouisfed.org/docs/fred/), and also provides several conveninent methods
for parsing and analyzing point-in-time data (i.e. historic data revisions) from [ALFRED](http://research.stlouisfed.org/tips/alfred/)

`fredapi` makes use of `pandas` and returns data to you in a `pandas` `Series` or `DataFrame`

## Installation

```sh
pip install fredapi
```
or
```sh
conda install fredapi
```

## Basic Usage

First you need an API key, you can [apply for one](http://api.stlouisfed.org/api_key.html) for free on the FRED website.
Once you have your API key, you can set it in one of three ways:

* set it to the evironment variable FRED_API_KEY
* save it to a file and use the 'api_key_file' parameter
* pass it directly as the 'api_key' parameter

```python
from fredapi import Fred
fred = Fred(api_key='insert api key here')
data = fred.get_series('SP500')
```

## Working with data revisions
Many economic data series contain frequent revisions. `fredapi` provides several convenient methods for handling data revisions and answering the quesion of what-data-was-known-when.

In [ALFRED](http://research.stlouisfed.org/tips/alfred/) there is the concept of a *vintage* date. Basically every *observation* can have three dates associated with it: *date*, *realtime_start* and *realtime_end*. 

- date: the date the value is for
- realtime_start: the first date the value is valid
- realitime_end: the last date the value is valid

For instance, there has been three observations (data points) for the GDP of 2014 Q1:

```xml
<observation realtime_start="2014-04-30" realtime_end="2014-05-28" date="2014-01-01" value="17149.6"/>
<observation realtime_start="2014-05-29" realtime_end="2014-06-24" date="2014-01-01" value="17101.3"/>
<observation realtime_start="2014-06-25" realtime_end="2014-07-29" date="2014-01-01" value="17016.0"/>
```

This means the GDP value for Q1 2014 has been released three times. First release was on 4/30/2014 for a value of 17149.6, and then there have been two revisions on 5/29/2014 and 6/25/2014 for revised values of 17101.3 and 17016.0, respectively.

### Get first data release only (i.e. ignore revisions)

### Get latest data

### Get latest data known on a given date

### Get all data release dates

## Dependencies
- [pandas](http://pandas.pydata.org/)
- [python-dateutil](http://labix.org/python-dateutil)
