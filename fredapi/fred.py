import os
import sys
if sys.version_info[0] >= 3:
    from urllib.request import urlopen
    from urllib.parse import quote_plus
else:
    from urllib2 import urlopen
    from urllib import quote_plus

import xml.etree.ElementTree as ET
from dateutil.parser import parse
import pandas as pd


class Fred(object):
    earliest_realtime_start = '1776-07-04'
    latest_realtime_end = '9999-12-31'
    nan_char = '.'

    def __init__(self,
                 api_key=None,
                 api_key_file=None):
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
            raise ValueError("You need to set a valid API key. You can set it in 3 ways: pass the string with api_key, "
                             "or set api_key_file to a file with the api key in the first line, or set the environment "
                             "variable 'FRED_API_KEY' to the value of your api key. You can sign up for a free api key "
                             "on the Fred website at http://research.stlouisfed.org/fred2/")

    def __fetch_data(self, url):
        response = urlopen(url)
        root = ET.fromstring(response.read())
        return root

    def get_series_info(self, series_id):
        url = "http://api.stlouisfed.org/fred/series?series_id=%s&api_key=%s" % (series_id, self.api_key)
        root = self.__fetch_data(url)
        return root.getchildren()[0].attrib
    
    def get_series(self, series_id):
        url = "http://api.stlouisfed.org/fred/series/observations?series_id=%s&api_key=%s" % (series_id, self.api_key)
        root = self.__fetch_data(url)
        data = {}
        for child in root.getchildren():
            val = child.get('value')
            if val == self.nan_char:
                val = float('NaN')
            else:
                val = float(val)
            data[parse(child.get('date'))] = val
        return pd.Series(data)
    
    def get_series_latest_release(self, series_id):
        return self.get_series(series_id)

    def get_series_first_release(self, series_id):
        df = self.get_series_all_releases(series_id)
        first_release = df.groupby('date').head(1)
        return first_release.set_index('date')['value']

    def get_series_as_of_date(self, series_id, as_of_date):
        as_of_date = pd.to_datetime(as_of_date)
        df = self.get_series_all_releases(series_id)
        return df[df['realtime_start'] <= as_of_date]

    def get_series_all_releases(self, series_id):
        url = "http://api.stlouisfed.org/fred/series/observations?series_id=%s&api_key=%s&realtime_start=%s&realtime_end=%s" % (series_id,
                                                                                                                                self.api_key,
                                                                                                                                self.earliest_realtime_start,
                                                                                                                                self.latest_realtime_end)
        root = self.__fetch_data(url)
        data = {}
        i = 0
        for child in root.getchildren():
            val = child.get('value')
            if val == self.nan_char:
                val = float('NaN')
            else:
                val = float(val)
            realtime_start = parse(child.get('realtime_start'))
            # realtime_end = parse(child.get('realtime_end'))
            date = parse(child.get('date'))
            
            data[i] = {'realtime_start': realtime_start,
                       # 'realtime_end': realtime_end,
                       'date': date,
                       'value': val}
            i += 1
        data = pd.DataFrame(data).T
        return data

    def get_series_vintage_dates(self, series_id):
        url = "http://api.stlouisfed.org/fred/series/vintagedates?series_id=%s&api_key=%s" % (series_id, self.api_key)
        root = self.__fetch_data(url)
        dates = []
        for child in root.getchildren():
            dates.append(parse(child.text))
        return dates

    def search(self, text, fulltext_search=True, limit=100):
        import urllib
        url = "http://api.stlouisfed.org/fred/series/search?search_text=%s&api_key=%s" % (quote_plus(text), self.api_key)
        root = self.__fetch_data(url)

        series_ids = []
        data = {}

        for child in root.getchildren():
            series_id = child.get('id')
            series_ids.append(series_id)
            data[series_id] = {"id": series_id}
            fields = ["realtime_start", "realtime_end", "title", "observation_start", "observation_end",
                      "frequency", "frequency_short", "units", "units_short", "seasonal_adjustment",
                      "seasonal_adjustment_short", "last_updated", "popularity", "notes"]
            for field in fields:
                data[series_id][field] = child.get(field)

        data = pd.DataFrame(data, columns=series_ids).T
        # parse datetime columns
        for field in ["realtime_start", "realtime_end", "observation_start", "observation_end", "last_updated"]:
            data[field] = data[field].apply(parse)
        # set index name
        data.index.name = 'series id'
        return data
