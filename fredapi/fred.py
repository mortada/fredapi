
import os
import sys
import xml.etree.ElementTree as ET
if sys.version_info[0] >= 3:
    import urllib.request as url_request
    import urllib.parse as url_parse
    import urllib.error as url_error
else:
    import urllib2 as url_request
    import urllib as url_parse
    import urllib2 as url_error

import pandas as pd

urlopen = url_request.urlopen
quote_plus = url_parse.quote_plus
urlencode = url_parse.urlencode
HTTPError = url_error.HTTPError


class Fred(object):
    earliest_realtime_start = '1776-07-04'
    latest_realtime_end = '9999-12-31'
    nan_char = '.'
    max_results_per_request = 1000
    root_url = 'https://api.stlouisfed.org/fred'

    def __init__(self,
                 api_key=None,
                 api_key_file=None):
        """
        Initialize the Fred class that provides useful functions to query the Fred dataset. You need to specify a valid
        API key in one of 3 ways: pass the string via api_key, or set api_key_file to a file with the api key in the
        first line, or set the environment variable 'FRED_API_KEY' to the value of your api key. You can sign up for a
        free api key on the Fred website at http://research.stlouisfed.org/fred2/
        """
        self.api_key = None
        if api_key is not None:
            self.api_key = api_key
        elif api_key_file is not None:
            f = open(api_key_file, 'r')
            self.api_key = f.readline().strip()
            f.close()
        else:
            self.api_key = os.environ.get('FRED_API_KEY')

        if self.api_key is None:
            import textwrap
            raise ValueError(textwrap.dedent("""\
                    You need to set a valid API key. You can set it in 3 ways:
                    pass the string with api_key, or set api_key_file to a
                    file with the api key in the first line, or set the
                    environment variable 'FRED_API_KEY' to the value of your
                    api key. You can sign up for a free api key on the Fred
                    website at http://research.stlouisfed.org/fred2/"""))

    def __fetch_data(self, url):
        """
        helper function for fetching data given a request URL
        """
        url += '&api_key=' + self.api_key
        try:
            response = urlopen(url)
            root = ET.fromstring(response.read())
        except HTTPError as exc:
            root = ET.fromstring(exc.read())
            raise ValueError(root.get('message'))
        return root

    def _parse(self, date_str, format='%Y-%m-%d'):
        """
        helper function for parsing FRED date string into datetime
        """
        rv = pd.to_datetime(date_str, format=format)
        if hasattr(rv, 'to_pydatetime'):
            rv = rv.to_pydatetime()
        return rv

    def get_series_info(self, series_id):
        """
        Get information about a series such as its title, frequency, observation start/end dates, units, notes, etc.

        Parameters
        ----------
        series_id : str
            Fred series id such as 'CPIAUCSL'

        Returns
        -------
        info : Series
            a pandas Series containing information about the Fred series
        """
        url = "%s/series?series_id=%s" % (self.root_url, series_id)
        root = self.__fetch_data(url)
        if root is None or not len(root):
            raise ValueError('No info exists for series id: ' + series_id)
        info = pd.Series(root.getchildren()[0].attrib)
        return info

    def get_series(self, series_id, observation_start=None, observation_end=None, **kwargs):
        """
        Get data for a Fred series id. This fetches the latest known data, and is equivalent to get_series_latest_release()

        Parameters
        ----------
        series_id : str
            Fred series id such as 'CPIAUCSL'
        observation_start : datetime or datetime-like str such as '7/1/2014', optional
            earliest observation date
        observation_end : datetime or datetime-like str such as '7/1/2014', optional
            latest observation date
        kwargs : additional parameters
            Any additional parameters supported by FRED. You can see https://api.stlouisfed.org/docs/fred/series_observations.html for the full list

        Returns
        -------
        data : Series
            a Series where each index is the observation date and the value is the data for the Fred series
        """
        url = "%s/series/observations?series_id=%s" % (self.root_url, series_id)
        if observation_start is not None:
            observation_start = pd.to_datetime(observation_start,
                                               errors='raise')
            url += '&observation_start=' + observation_start.strftime('%Y-%m-%d')
        if observation_end is not None:
            observation_end = pd.to_datetime(observation_end, errors='raise')
            url += '&observation_end=' + observation_end.strftime('%Y-%m-%d')
        if kwargs.keys():
            url += '&' + urlencode(kwargs)
        root = self.__fetch_data(url)
        if root is None:
            raise ValueError('No data exists for series id: ' + series_id)
        data = {}
        for child in root.getchildren():
            val = child.get('value')
            if val == self.nan_char:
                val = float('NaN')
            else:
                val = float(val)
            data[self._parse(child.get('date'))] = val
        return pd.Series(data)

    def get_series_latest_release(self, series_id):
        """
        Get data for a Fred series id. This fetches the latest known data, and is equivalent to get_series()

        Parameters
        ----------
        series_id : str
            Fred series id such as 'CPIAUCSL'

        Returns
        -------
        info : Series
            a Series where each index is the observation date and the value is the data for the Fred series
        """
        return self.get_series(series_id)

    def get_series_first_release(self, series_id):
        """
        Get first-release data for a Fred series id. This ignores any revision to the data series. For instance,
        The US GDP for Q1 2014 was first released to be 17149.6, and then later revised to 17101.3, and 17016.0.
        This will ignore revisions after the first release.

        Parameters
        ----------
        series_id : str
            Fred series id such as 'GDP'

        Returns
        -------
        data : Series
            a Series where each index is the observation date and the value is the data for the Fred series
        """
        df = self.get_series_all_releases(series_id)
        first_release = df.groupby('date').head(1)
        data = first_release.set_index('date')['value']
        return data

    def get_series_as_of_date(self, series_id, as_of_date):
        """
        Get latest data for a Fred series id as known on a particular date. This includes any revision to the data series
        before or on as_of_date, but ignores any revision on dates after as_of_date.

        Parameters
        ----------
        series_id : str
            Fred series id such as 'GDP'
        as_of_date : datetime, or datetime-like str such as '10/25/2014'
            Include data revisions on or before this date, and ignore revisions afterwards

        Returns
        -------
        data : Series
            a Series where each index is the observation date and the value is the data for the Fred series
        """
        as_of_date = pd.to_datetime(as_of_date)
        df = self.get_series_all_releases(series_id)
        data = df[df['realtime_start'] <= as_of_date]
        return data

    def get_series_all_releases(self, series_id):
        """
        Get all data for a Fred series id including first releases and all revisions. This returns a DataFrame
        with three columns: 'date', 'realtime_start', and 'value'. For instance, the US GDP for Q4 2013 was first released
        to be 17102.5 on 2014-01-30, and then revised to 17080.7 on 2014-02-28, and then revised to 17089.6 on
        2014-03-27. You will therefore get three rows with the same 'date' (observation date) of 2013-10-01 but three
        different 'realtime_start' of 2014-01-30, 2014-02-28, and 2014-03-27 with corresponding 'value' of 17102.5, 17080.7
        and 17089.6

        Parameters
        ----------
        series_id : str
            Fred series id such as 'GDP'

        Returns
        -------
        data : DataFrame
            a DataFrame with columns 'date', 'realtime_start' and 'value' where 'date' is the observation period and 'realtime_start'
            is when the corresponding value (either first release or revision) is reported.
        """
        url = "%s/series/observations?series_id=%s&realtime_start=%s&realtime_end=%s" % (self.root_url,
                                                                                         series_id,
                                                                                         self.earliest_realtime_start,
                                                                                         self.latest_realtime_end)
        root = self.__fetch_data(url)
        if root is None:
            raise ValueError('No data exists for series id: ' + series_id)
        data = {}
        i = 0
        for child in root.getchildren():
            val = child.get('value')
            if val == self.nan_char:
                val = float('NaN')
            else:
                val = float(val)
            realtime_start = self._parse(child.get('realtime_start'))
            # realtime_end = self._parse(child.get('realtime_end'))
            date = self._parse(child.get('date'))

            data[i] = {'realtime_start': realtime_start,
                       # 'realtime_end': realtime_end,
                       'date': date,
                       'value': val}
            i += 1
        data = pd.DataFrame(data).T
        return data

    def get_series_vintage_dates(self, series_id):
        """
        Get a list of vintage dates for a series. Vintage dates are the dates in history when a
        series' data values were revised or new data values were released.

        Parameters
        ----------
        series_id : str
            Fred series id such as 'CPIAUCSL'

        Returns
        -------
        dates : list
            list of vintage dates
        """
        url = "%s/series/vintagedates?series_id=%s" % (self.root_url, series_id)
        root = self.__fetch_data(url)
        if root is None:
            raise ValueError('No vintage date exists for series id: ' + series_id)
        dates = []
        for child in root.getchildren():
            dates.append(self._parse(child.text))
        return dates

    def __do_series_search(self, url):
        """
        helper function for making one HTTP request for data, and parsing the returned results into a DataFrame
        """
        root = self.__fetch_data(url)

        series_ids = []
        data = {}

        num_results_returned = 0  # number of results returned in this HTTP request
        num_results_total = int(root.get('count'))  # total number of results, this can be larger than number of results returned
        for child in root.getchildren():
            num_results_returned += 1
            series_id = child.get('id')
            series_ids.append(series_id)
            data[series_id] = {"id": series_id}
            fields = ["realtime_start", "realtime_end", "title", "observation_start", "observation_end",
                      "frequency", "frequency_short", "units", "units_short", "seasonal_adjustment",
                      "seasonal_adjustment_short", "last_updated", "popularity", "notes"]
            for field in fields:
                data[series_id][field] = child.get(field)

        if num_results_returned > 0:
            data = pd.DataFrame(data, columns=series_ids).T
            # parse datetime columns
            for field in ["realtime_start", "realtime_end", "observation_start", "observation_end", "last_updated"]:
                data[field] = data[field].apply(self._parse, format=None)
            # set index name
            data.index.name = 'series id'
        else:
            data = None
        return data, num_results_total

    def __get_search_results(self, url, limit, order_by, sort_order, filter):
        """
        helper function for getting search results up to specified limit on the number of results. The Fred HTTP API
        truncates to 1000 results per request, so this may issue multiple HTTP requests to obtain more available data.
        """

        order_by_options = ['search_rank', 'series_id', 'title', 'units', 'frequency',
                            'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated',
                            'observation_start', 'observation_end', 'popularity']
        if order_by is not None:
            if order_by in order_by_options:
                url = url + '&order_by=' + order_by
            else:
                raise ValueError('%s is not in the valid list of order_by options: %s' % (order_by, str(order_by_options)))

        if filter is not None:
            if len(filter) == 2:
                url = url + '&filter_variable=%s&filter_value=%s' % (filter[0], filter[1])
            else:
                raise ValueError('Filter should be a 2 item tuple like (filter_variable, filter_value)')

        sort_order_options = ['asc', 'desc']
        if sort_order is not None:
            if sort_order in sort_order_options:
                url = url + '&sort_order=' + sort_order
            else:
                raise ValueError('%s is not in the valid list of sort_order options: %s' % (sort_order, str(sort_order_options)))

        data, num_results_total = self.__do_series_search(url)
        if data is None:
            return data

        if limit == 0:
            max_results_needed = num_results_total
        else:
            max_results_needed = limit

        if max_results_needed > self.max_results_per_request:
            for i in range(1, max_results_needed // self.max_results_per_request + 1):
                offset = i * self.max_results_per_request
                next_data, _ = self.__do_series_search(url + '&offset=' + str(offset))
                data = data.append(next_data)
        return data.head(max_results_needed)

    def search(self, text, limit=1000, order_by=None, sort_order=None, filter=None):
        """
        Do a fulltext search for series in the Fred dataset. Returns information about matching series in a DataFrame.

        Parameters
        ----------
        text : str
            text to do fulltext search on, e.g., 'Real GDP'
        limit : int, optional
            limit the number of results to this value. If limit is 0, it means fetching all results without limit.
        order_by : str, optional
            order the results by a criterion. Valid options are 'search_rank', 'series_id', 'title', 'units', 'frequency',
            'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end',
            'popularity'
        sort_order : str, optional
            sort the results by ascending or descending order. Valid options are 'asc' or 'desc'
        filter : tuple, optional
            filters the results. Expects a tuple like (filter_variable, filter_value).
            Valid filter_variable values are 'frequency', 'units', and 'seasonal_adjustment'

        Returns
        -------
        info : DataFrame
            a DataFrame containing information about the matching Fred series
        """
        url = "%s/series/search?search_text=%s&" % (self.root_url,
                                                    quote_plus(text))
        info = self.__get_search_results(url, limit, order_by, sort_order, filter)
        return info

    def search_by_release(self, release_id, limit=0, order_by=None, sort_order=None, filter=None):
        """
        Search for series that belongs to a release id. Returns information about matching series in a DataFrame.

        Parameters
        ----------
        release_id : int
            release id, e.g., 151
        limit : int, optional
            limit the number of results to this value. If limit is 0, it means fetching all results without limit.
        order_by : str, optional
            order the results by a criterion. Valid options are 'search_rank', 'series_id', 'title', 'units', 'frequency',
            'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end',
            'popularity'
        sort_order : str, optional
            sort the results by ascending or descending order. Valid options are 'asc' or 'desc'
        filter : tuple, optional
            filters the results. Expects a tuple like (filter_variable, filter_value).
            Valid filter_variable values are 'frequency', 'units', and 'seasonal_adjustment'

        Returns
        -------
        info : DataFrame
            a DataFrame containing information about the matching Fred series
        """
        url = "%s/release/series?release_id=%d" % (self.root_url, release_id)
        info = self.__get_search_results(url, limit, order_by, sort_order, filter)
        if info is None:
            raise ValueError('No series exists for release id: ' + str(release_id))
        return info

    def search_by_category(self, category_id, limit=0, order_by=None, sort_order=None, filter=None):
        """
        Search for series that belongs to a category id. Returns information about matching series in a DataFrame.

        Parameters
        ----------
        category_id : int
            category id, e.g., 32145
        limit : int, optional
            limit the number of results to this value. If limit is 0, it means fetching all results without limit.
        order_by : str, optional
            order the results by a criterion. Valid options are 'search_rank', 'series_id', 'title', 'units', 'frequency',
            'seasonal_adjustment', 'realtime_start', 'realtime_end', 'last_updated', 'observation_start', 'observation_end',
            'popularity'
        sort_order : str, optional
            sort the results by ascending or descending order. Valid options are 'asc' or 'desc'
        filter : tuple, optional
            filters the results. Expects a tuple like (filter_variable, filter_value).
            Valid filter_variable values are 'frequency', 'units', and 'seasonal_adjustment'

        Returns
        -------
        info : DataFrame
            a DataFrame containing information about the matching Fred series
        """
        url = "%s/category/series?category_id=%d&" % (self.root_url,
                                                      category_id)
        info = self.__get_search_results(url, limit, order_by, sort_order, filter)
        if info is None:
            raise ValueError('No series exists for category id: ' + str(category_id))
        return info
