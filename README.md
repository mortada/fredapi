# fredapi: Python API for FRED (Federal Reserve Economic Data)
<!-- badges: start -->
[![Pypi version](https://img.shields.io/pypi/v/fredapi.svg)](https://pypi.python.org/pypi/fredapi/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![GitHub Actions](https://img.shields.io/badge/githubactions-%232671E5.svg?style=flat&logo=githubactions&logoColor=white)
![Interrogate](docs/_static/interrogate_badge.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<!-- badges: end -->

`fredapi` is a Python API for the [FRED](http://research.stlouisfed.org/fred2/) data provided by the
Federal Reserve Bank of St. Louis. `fredapi` provides a wrapper in python to the
[FRED web service](http://api.stlouisfed.org/docs/fred/), and also provides several convenient methods
for parsing and analyzing point-in-time data (i.e. historic data revisions) from [ALFRED](http://research.stlouisfed.org/tips/alfred/)

`fredapi` makes use of `pandas` and returns data to you in a `pandas` `Series` or `DataFrame`

## Installation

```sh
pip install fredapi
```

## Basic Usage

First you need an API key, you can [apply for one](http://api.stlouisfed.org/api_key.html) for free on the FRED website.
Once you have your API key, you can set it in one of three ways:

* set it to the environment variable FRED_API_KEY
* save it to a file and use the 'api_key_file' parameter
* pass it directly as the 'api_key' parameter

```python
from fredapi import Fred
fred = Fred(api_key='insert api key here')
data = fred.get_series('SP500')
```

## Documentation

For information on `fredapi` functionality, such as working with data revisions, [checkout the documentation](https://gw-moore.github.io/fredapi/index.html)

## More Examples
- [@mortada](https://github.com/mortada) wrote a [blog post with more examples](http://mortada.net/python-api-for-fred.html) written in an `IPython` notebook
