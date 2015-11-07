
[![fredapi pypi page](https://img.shields.io/pypi/dm/fredapi.svg)](https://pypi.python.org/pypi/fredapi)

# fredapi: Python API for FRED (Federal Reserve Economic Data)

`fredapi` is a Python API for the [FRED](http://research.stlouisfed.org/fred2/) data provided by the
Federal Reserve Bank of St. Louis. `fredapi` provides a wrapper in python to the 
[FRED web service](http://api.stlouisfed.org/docs/fred/), and also provides several conveninent methods
for parsing and analyzing point-in-time data (i.e. historic data revisions) from [ALFRED](http://research.stlouisfed.org/tips/alfred/)

`fredapi` makes use of `pandas` and returns data to you in a `pandas` `Series` or `DataFrame`

## Installation

```sh
pip install fredapi
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
- realtime_end: the last date the value is valid

For instance, there has been three observations (data points) for the GDP of 2014 Q1:

```xml
<observation realtime_start="2014-04-30" realtime_end="2014-05-28" date="2014-01-01" value="17149.6"/>
<observation realtime_start="2014-05-29" realtime_end="2014-06-24" date="2014-01-01" value="17101.3"/>
<observation realtime_start="2014-06-25" realtime_end="2014-07-29" date="2014-01-01" value="17016.0"/>
```

This means the GDP value for Q1 2014 has been released three times. First release was on 4/30/2014 for a value of 17149.6, and then there have been two revisions on 5/29/2014 and 6/25/2014 for revised values of 17101.3 and 17016.0, respectively.

If you pass realtime_start and/or realtime_end to `get_series`, you will get a pandas.DataFrame with a pandas.MultiIndex instead of a pandas.Series.

For instance, with observation_start and observation_end set to 2015-01-01 and
realtime_start set to 2015-01-01, one will get:
```
                                 GDP
obs_date   rt_start   rt_end
2015-01-01 2015-04-29 2015-05-28 17710.0
           2015-05-29 2015-06-23 17665.0
           2015-06-24 9999-12-31 17693.3
```

### Get first data release only (i.e. ignore revisions)

```python
data = fred.get_series_first_release('GDP')
data.tail()
```
this outputs:

```sh
date
2013-04-01    16633.4
2013-07-01    16857.6
2013-10-01    17102.5
2014-01-01    17149.6
2014-04-01    17294.7
Name: value, dtype: object
```

### Get latest data
Note that this is the same as simply calling `get_series()`
```python
data = fred.get_series_latest_release('GDP')
data.tail()
```
this outputs:
```
2013-04-01    16619.2
2013-07-01    16872.3
2013-10-01    17078.3
2014-01-01    17044.0
2014-04-01    17294.7
dtype: float64
```

### Get latest data for multiple series for the latest release
```python
data = fred.get_dataframe(['SP500', 'GDP'], frequency='q')
data.tail()
```
this outputs:
```
              SP500      GDP
2014-07-31  1975.91  17599.8
2014-10-31  2009.34  17703.7
2015-01-31  2063.69  17693.3
dtype: float64
```

Note that if you do not specify the frequency each series will be output on its
own intrinsic frequency introducing NaN in the dataframe.
```python
data = fred.get_dataframe(['GDP', 'PAYEMS'])
data.tail()
```
outputs:
```
                GDP  PAYEMS
2014-07-31  17599.8  139156
2014-08-31      NaN  139369
2014-09-30      NaN  139619
2014-10-31  17703.7  139840
2014-11-30      NaN  140263
2014-12-31      NaN  140592
2015-01-31  17693.3  140793
```


### Get latest data known on a given date

```python
fred.get_series_as_of_date('GDP', '6/1/2014')
```
this outputs:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>realtime_start</th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2237</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-01-30 00:00:00</td>
      <td> 17102.5</td>
    </tr>
    <tr>
      <th>2238</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-02-28 00:00:00</td>
      <td> 17080.7</td>
    </tr>
    <tr>
      <th>2239</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-03-27 00:00:00</td>
      <td> 17089.6</td>
    </tr>
    <tr>
      <th>2241</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-04-30 00:00:00</td>
      <td> 17149.6</td>
    </tr>
    <tr>
      <th>2242</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-05-29 00:00:00</td>
      <td> 17101.3</td>
    </tr>
  </tbody>
</table>

### Get all data release dates
This returns a `DataFrame` with all the data from ALFRED

```python
df = fred.get_series_all_releases('GDP')
df.tail()
```
this outputs:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>realtime_start</th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2236</th>
      <td> 2013-07-01 00:00:00</td>
      <td> 2014-07-30 00:00:00</td>
      <td> 16872.3</td>
    </tr>
    <tr>
      <th>2237</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-01-30 00:00:00</td>
      <td> 17102.5</td>
    </tr>
    <tr>
      <th>2238</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-02-28 00:00:00</td>
      <td> 17080.7</td>
    </tr>
    <tr>
      <th>2239</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-03-27 00:00:00</td>
      <td> 17089.6</td>
    </tr>
    <tr>
      <th>2240</th>
      <td> 2013-10-01 00:00:00</td>
      <td> 2014-07-30 00:00:00</td>
      <td> 17078.3</td>
    </tr>
    <tr>
      <th>2241</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-04-30 00:00:00</td>
      <td> 17149.6</td>
    </tr>
    <tr>
      <th>2242</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-05-29 00:00:00</td>
      <td> 17101.3</td>
    </tr>
    <tr>
      <th>2243</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-06-25 00:00:00</td>
      <td>   17016</td>
    </tr>
    <tr>
      <th>2244</th>
      <td> 2014-01-01 00:00:00</td>
      <td> 2014-07-30 00:00:00</td>
      <td>   17044</td>
    </tr>
    <tr>
      <th>2245</th>
      <td> 2014-04-01 00:00:00</td>
      <td> 2014-07-30 00:00:00</td>
      <td> 17294.7</td>
    </tr>
  </tbody>
</table>

### Get multiple series at multiple point in time

This work the same way as for the latest release, one just adds either
realtime_start, realtime_end, or both.

```python
data = fred.get_dataframe(['GDP', 'CP'], observation_start='7/1/2014',
                          observation_end='1/1/2015', realtime_start='7/1/2014')
data.tail()
```
outputs:
```
                                      GDP      CP
obs_date   rt_start   rt_end                     
2014-07-01 2014-10-30 2014-11-24  17535.4     NaN
           2014-11-25 2014-12-22  17555.2  1872.7
           2014-12-23 NaT         17599.8     NaN
                      2015-07-29      NaN  1894.6
           2015-07-30 NaT             NaN  1761.1
2014-10-01 2015-01-30 2015-02-26  17710.7     NaN
           2015-02-27 2015-03-26  17701.3     NaN
           2015-03-27 NaT         17703.7     NaN
                      2015-07-29      NaN  1837.5
           2015-07-30 NaT             NaN  1700.5
2015-01-01 2015-04-29 2015-05-28  17710.0     NaN
           2015-05-29 2015-06-23  17665.0  1893.8
           2015-06-24 NaT         17693.3     NaN
                      2015-07-29      NaN  1891.2
           2015-07-30 NaT             NaN  1734.5''')
```

### Get all vintage dates
```python
from __future__ import print_function
vintage_dates = fred.get_series_vintage_dates('GDP')
for dt in vintage_dates[-5:]:
    print(dt.strftime('%Y-%m-%d'))
```
this outputs:
```
2014-03-27
2014-04-30
2014-05-29
2014-06-25
2014-07-30
```

### Search for data series

You can always search for data series on the FRED website. But sometimes it can be more convenient to search programmatically.
`fredapi` provides a `search()` method that does a fulltext search and returns a `DataFrame` of results.

```python
fred.search('potential gdp').T
```
this outputs:

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>series id</th>
      <th>GDPPOT</th>
      <th>NGDPPOT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>frequency</th>
      <td>Quarterly</td>
      <td>Quarterly</td>
    </tr>
    <tr>
      <th>frequency_short</th>
      <td>Q</td>
      <td>Q</td>
    </tr>
    <tr>
      <th>id</th>
      <td>GDPPOT</td>
      <td>NGDPPOT</td>
    </tr>
    <tr>
      <th>last_updated</th>
      <td>2014-02-04 10:06:03-06:00</td>
      <td>2014-02-04 10:06:03-06:00</td>
    </tr>
    <tr>
      <th>notes</th>
      <td> Real potential GDP is the CBO&#39;s estimate of the output the economy would produce with a high rate of use of its capital and labor resources. The data is adjusted to remove the effects of inflation.</td>
      <td>None</td>
    </tr>
    <tr>
      <th>observation_end</th>
      <td>2024-10-01 00:00:00</td>
      <td>2024-10-01 00:00:00</td>
    </tr>
    <tr>
      <th>observation_start</th>
      <td>1949-01-01 00:00:00</td>
      <td>1949-01-01 00:00:00</td>
    </tr>
    <tr>
      <th>popularity</th>
      <td>72</td>
      <td>61</td>
    </tr>
    <tr>
      <th>realtime_end</th>
      <td>2014-08-23 00:00:00</td>
      <td>2014-08-23 00:00:00</td>
    </tr>
    <tr>
      <th>realtime_start</th>
      <td>2014-08-23 00:00:00</td>
      <td>2014-08-23 00:00:00</td>
    </tr>
    <tr>
      <th>seasonal_adjustment</th>
      <td>Not Seasonally Adjusted</td>
      <td>Not Seasonally Adjusted</td>
    </tr>
    <tr>
      <th>seasonal_adjustment_short</th>
      <td>NSA</td>
      <td>NSA</td>
    </tr>
    <tr>
      <th>title</th>
      <td>Real Potential Gross Domestic Product</td>
      <td>Nominal Potential Gross Domestic Product</td>
    </tr>
    <tr>
      <th>units</th>
      <td>Billions of Chained 2009 Dollars</td>
      <td>Billions of Dollars</td>
    </tr>
    <tr>
      <th>units_short</th>
      <td>Bil. of Chn. 2009 &#36;</td>
      <td>Bil. of &#36;</td>
    </tr>
  </tbody>
</table>

## Dependencies
- [pandas](http://pandas.pydata.org/)

## More Examples
- I have a [blog post with more examples](http://mortada.net/python-api-for-fred.html) written in an `IPython` notebook
