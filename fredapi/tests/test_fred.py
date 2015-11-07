
from __future__ import unicode_literals

import sys
if sys.version_info[0] >= 3:
    unicode = str

import os
import io
import unittest
if sys.version_info < (3, 3):
    import mock  # pylint: disable=import-error
else:
    from unittest import mock  # pylint: disable=import-error
import datetime as dt
import textwrap
import contextlib

import fredapi
import fredapi.fred


# Change here if you want to make actual calls to Fred
# (https://api.stlouisfed.org/fred...)
# Make sure you FRED_API_KEY is set up and internet works.
fake_fred_call = True
fred_api_key = 'secret'
if not fake_fred_call:
    fred_api_key = fredapi.Fred().api_key

class HTTPCall(object):
    """Encapsulates faked Fred call data."""

    root_url = fredapi.Fred.root_url

    def __init__(self, rel_url, response=None, side_effect=None):
        """Construct HTTPCall from argument.

        Parameters:
        -----------
        rel_url: relative url to the root url for the call.
        response: response to the call if any.
        side_effect: side_effect to the call if any.

        """
        self.url = '{}/{}&api_key={}'.format(self.root_url, rel_url,
                                             fred_api_key)
        self.response = response
        self.side_effect = side_effect


sp500_info_call = HTTPCall('series?series_id=SP500',
                           response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <seriess realtime_start="2015-07-18" realtime_end="2015-07-18">
      <series id="SP500" realtime_start="2015-07-18"
                         realtime_end="2015-07-18"
                         title="S&amp;P 500"
                         observation_start="2005-07-18"
                         observation_end="2015-07-17" frequency="Daily"
                         frequency_short="D" units="Index"
                         units_short="Index"
                         seasonal_adjustment="Not Seasonally Adjusted"
                         seasonal_adjustment_short="NSA"
                         last_updated="2015-07-17 17:24:36-05"
                         popularity="82" notes="..." />
    </seriess>'''))
payems_info_call = HTTPCall('series?series_id=PAYEMS',
                            response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <seriess realtime_start="2015-06-28" realtime_end="2015-06-28">
      <series id="PAYEMS" realtime_start="2015-06-28" realtime_end="2015-06-28"
              title="All Employees: Total Nonfarm Payrolls"
              observation_start="1939-01-01" observation_end="2015-05-01"
              frequency="Monthly" frequency_short="M"
              units="Thousands of Persons" units_short="Thous. of Persons"
              seasonal_adjustment="Seasonally Adjusted"
              seasonal_adjustment_short="SA"
              last_updated="2015-06-05 08:47:20-05"
              popularity="86" notes="..." />
    </seriess>'''))
cp_info_call = HTTPCall('series?series_id=CP',
                        response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <seriess realtime_start="2015-10-17" realtime_end="2015-10-17">
        <series id="CP" realtime_start="2015-10-17" realtime_end="2015-10-17"
                title="Corporate Profits After Tax (without IVA and CCAdj)"
                observation_start="1947-01-01" observation_end="2015-04-01"
                frequency="Quarterly" frequency_short="Q"
                units="Billions of Dollars" units_short="Bil. of $"
                seasonal_adjustment="Seasonally Adjusted Annual Rate"
                seasonal_adjustment_short="SAAR"
                last_updated="2015-09-25 08:06:11-05" popularity="73"
                notes="BEA Account Code: A055RC1"/>
    </seriess>
    '''))
gdp_info_call = HTTPCall('series?series_id=GDP',
                                 response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <seriess realtime_start="2015-07-19" realtime_end="2015-07-19">
      <series id="GDP" realtime_start="2015-07-19" realtime_end="2015-07-19"
              title="Gross Domestic Product" observation_start="1947-01-01"
              observation_end="2015-01-01" frequency="Quarterly"
              frequency_short="Q" units="Billions of Dollars"
              units_short="Bil. of $"
              seasonal_adjustment="Seasonally Adjusted Annual Rate"
              seasonal_adjustment_short="SAAR"
              last_updated="2015-06-24 08:06:09-05" popularity="91"
              notes="BEA Account Code: A191RC1..." />
    </seriess>
    '''))

sp500_obs_call = HTTPCall('series/observations?series_id=SP500&{}&{}'.
                          format('observation_start=2014-09-02',
                                 'observation_end=2014-09-05'),
                          response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2015-06-28" realtime_end="2015-06-28"
                  observation_start="2014-09-02"
                  observation_end="2014-09-05" units="lin"
                  output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc"
                  count="4" offset="0" limit="100000">
      <observation realtime_start="2015-06-28" realtime_end="2015-06-28"
                   date="2014-09-02" value="2002.28"/>
      <observation realtime_start="2015-06-28" realtime_end="2015-06-28"
                   date="2014-09-03" value="2000.72"/>
      <observation realtime_start="2015-06-28" realtime_end="2015-06-28"
                   date="2014-09-04" value="1997.65"/>
      <observation realtime_start="2015-06-28" realtime_end="2015-06-28"
                   date="2014-09-05" value="2007.71"/>
    </observations>'''))
search_call = HTTPCall('release/series?release_id=175&' +
                       'order_by=series_id&sort_order=asc',
                       response = textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8"?>
    <seriess realtime_start="2015-07-19" realtime_end="2015-07-19"
             order_by="series_id" sort_order="asc" count="6164"
             offset="0" limit="1000">
      <series id="PCPI01001" realtime_start="2015-07-19"
              realtime_end="2015-07-19"
              title="Per Capita Personal Income in Autauga County, AL"
              observation_start="1969-01-01" observation_end="2013-01-01"
              frequency="Annual" frequency_short="A" units="Dollars"
              units_short="$" seasonal_adjustment="Not Seasonally Adjusted"
              seasonal_adjustment_short="NSA"
              last_updated="2015-01-29 12:10:21-06"
              popularity="0" notes="..." />
      <series id="PCPI01003" realtime_start="2015-07-19"
              realtime_end="2015-07-19"
              title="Per Capita Personal Income in Baldwin County, AL"
              observation_start="1969-01-01" observation_end="2013-01-01"
              frequency="Annual" frequency_short="A" units="Dollars"
              units_short="$" seasonal_adjustment="Not Seasonally Adjusted"
              seasonal_adjustment_short="NSA"
              last_updated="2015-01-29 12:10:21-06"
              popularity="0" notes="..." />
      <series id="PCPI01005" realtime_start="2015-07-19"
              realtime_end="2015-07-19"
              title="Per Capita Personal Income in Barbour County, AL"
              observation_start="1969-01-01" observation_end="2013-01-01"
              frequency="Annual" frequency_short="A" units="Dollars"
              units_short="$" seasonal_adjustment="Not Seasonally Adjusted"
              seasonal_adjustment_short="NSA"
              last_updated="2015-01-29 12:10:21-06"
              popularity="0" notes="..." />
      <!-- more series come here, but not useful for the test... -->
    </seriess>
    '''))
sp500_obs_q_call = HTTPCall('series/observations?series_id=SP500&{}&{}&{}'.
                          format('observation_start=2014-07-01',
                                 'observation_end=2015-01-01',
                                 'frequency=q'),
                          response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2015-07-19" realtime_end="2015-07-19"
                  observation_start="2014-07-01" observation_end="2015-01-01"
                  units="lin" output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc" count="3"
                  offset="0" limit="100000">
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-07-01" value="1975.91"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-10-01" value="2009.34"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2015-01-01" value="2063.69"/>
    </observations>'''))
gdp_obs_q_call = HTTPCall('series/observations?series_id=GDP&{}&{}&{}'.
                          format('observation_start=2014-07-01',
                                 'observation_end=2015-01-01',
                                 'frequency=q'),
                          response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2015-07-19" realtime_end="2015-07-19"
                  observation_start="2014-07-01" observation_end="2015-01-01"
                  units="lin" output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc" count="3"
                  offset="0" limit="100000">
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-07-01" value="17599.8"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-10-01" value="17703.7"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2015-01-01" value="17693.3"/>
    </observations>
    '''))
payems_obs_call = HTTPCall('series/observations?{}&{}&{}'.
                                format('series_id=PAYEMS',
                                       'observation_start=2014-07-01',
                                       'observation_end=2015-01-01'),
                                response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2015-07-19" realtime_end="2015-07-19" observation_start="2014-07-01" observation_end="2015-01-01" units="lin" output_type="1" file_type="xml" order_by="observation_date" sort_order="asc" count="7" offset="0" limit="100000">
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-07-01" value="139156"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-08-01" value="139369"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-09-01" value="139619"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-10-01" value="139840"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-11-01" value="140263"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-12-01" value="140592"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2015-01-01" value="140793"/>
    </observations>
    '''))
gdp_obs_call = HTTPCall('series/observations?{}&{}&{}'.
                                format('series_id=GDP',
                                       'observation_start=2014-07-01',
                                       'observation_end=2015-01-01'),
                                response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2015-07-19" realtime_end="2015-07-19"
                  observation_start="2014-07-01" observation_end="2015-01-01"
                  units="lin" output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc" count="3"
                  offset="0" limit="100000">
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-07-01" value="17599.8"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2014-10-01" value="17703.7"/>
      <observation realtime_start="2015-07-19" realtime_end="2015-07-19"
                   date="2015-01-01" value="17693.3"/>
    </observations>
    '''))
gdp_obs_rt_call = HTTPCall('series/observations?{}&{}&{}&{}'.
                           format('series_id=GDP',
                                  'observation_start=2014-07-01',
                                  'observation_end=2015-01-01',
                                  'realtime_start=2014-07-01'),
                           response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2014-07-01" realtime_end="9999-12-31"
                  observation_start="2014-07-01" observation_end="2015-01-01"
                  units="lin" output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc" count="9"
                  offset="0" limit="100000">
      <observation realtime_start="2014-10-30" realtime_end="2014-11-24"
                   date="2014-07-01" value="17535.4"/>
      <observation realtime_start="2014-11-25" realtime_end="2014-12-22"
                   date="2014-07-01" value="17555.2"/>
      <observation realtime_start="2014-12-23" realtime_end="9999-12-31"
                   date="2014-07-01" value="17599.8"/>
      <observation realtime_start="2015-01-30" realtime_end="2015-02-26"
                   date="2014-10-01" value="17710.7"/>
      <observation realtime_start="2015-02-27" realtime_end="2015-03-26"
                   date="2014-10-01" value="17701.3"/>
      <observation realtime_start="2015-03-27" realtime_end="9999-12-31"
                   date="2014-10-01" value="17703.7"/>
      <observation realtime_start="2015-04-29" realtime_end="2015-05-28"
                   date="2015-01-01" value="17710.0"/>
      <observation realtime_start="2015-05-29" realtime_end="2015-06-23"
                   date="2015-01-01" value="17665.0"/>
      <observation realtime_start="2015-06-24" realtime_end="9999-12-31"
                   date="2015-01-01" value="17693.3"/>
    </observations>
    '''))
cp_obs_rt_call = HTTPCall('series/observations?{}&{}&{}&{}'.
                           format('series_id=CP',
                                  'observation_start=2014-07-01',
                                  'observation_end=2015-01-01',
                                  'realtime_start=2014-07-01'),
                           response=textwrap.dedent('''\
    <?xml version="1.0" encoding="utf-8" ?>
    <observations realtime_start="2014-07-01" realtime_end="9999-12-31"
                  observation_start="2014-07-01" observation_end="2015-01-01"
                  units="lin" output_type="1" file_type="xml"
                  order_by="observation_date" sort_order="asc" count="8"
                  offset="0" limit="100000">
      <observation realtime_start="2014-11-25" realtime_end="2014-12-22"
                   date="2014-07-01" value="1872.7"/>
      <observation realtime_start="2014-12-23" realtime_end="2015-07-29"
                   date="2014-07-01" value="1894.6"/>
      <observation realtime_start="2015-07-30" realtime_end="9999-12-31"
                   date="2014-07-01" value="1761.1"/>
      <observation realtime_start="2015-03-27" realtime_end="2015-07-29"
                   date="2014-10-01" value="1837.5"/>
      <observation realtime_start="2015-07-30" realtime_end="9999-12-31"
                   date="2014-10-01" value="1700.5"/>
      <observation realtime_start="2015-05-29" realtime_end="2015-06-23"
                   date="2015-01-01" value="1893.8"/>
      <observation realtime_start="2015-06-24" realtime_end="2015-07-29"
                   date="2015-01-01" value="1891.2"/>
      <observation realtime_start="2015-07-30" realtime_end="9999-12-31"
                   date="2015-01-01" value="1734.5"/>
    </observations>
    '''))


class TestFred(unittest.TestCase):

    """Test fredapi.Fred class.

    See setUp() to configure the tests to make internent requests or fake.

    """

    root_url = fredapi.Fred.root_url

    def setUp(self):
        """Set up test.

        If the FRED_API_KEY env variable is defined, we use it in the url to
        help with quick checks between what's expected and what's returned by
        Fred.

        Only go against Fred during tests if fake_fred_call variable is True.

        as results are subject to change and the tests should be runnable
        without an internet connection or a FRED api key so they can be
        run as part of automated continuous integration (e.g. travis-ci.org).

        """
        self.fred = fredapi.Fred(api_key=fred_api_key)
        self.fake_fred_call = fake_fred_call
        self.__original_urlopen = fredapi.fred.urlopen

    def tearDown(self):
        """Cleanup."""
        pass

    def prepare_urlopen(self, urlopen, http_response=None, side_effect=None):
        """Set urlopen to return http_response or the regular call."""
        if self.fake_fred_call:
            if http_response:
                urlopen.return_value.read.return_value = http_response
            elif side_effect:
                urlopen.return_value.read.side_effect = side_effect
        else:
            urlopen.side_effect = self.__original_urlopen

    @mock.patch('fredapi.fred.urlopen')
    def test_get_series(self, urlopen):
        """Test retrieval of series for SP500."""
        self.prepare_urlopen(urlopen,
                             http_response=sp500_obs_call.response)
        serie = self.fred.get_series('SP500', observation_start='9/2/2014',
                                     observation_end='9/5/2014')
        urlopen.assert_called_with(sp500_obs_call.url)
        self.assertEqual(serie.ix['9/2/2014'], 2002.28)
        self.assertEqual(len(serie), 4)

    @mock.patch('fredapi.fred.urlopen')
    def test_get_series_info_payem(self, urlopen):
        """Test retrieval of get_series_info for PAYEMS."""
        url = payems_info_call.url
        http_response = payems_info_call.response
        self.prepare_urlopen(urlopen, http_response=http_response)
        info = self.fred.get_series_info('PAYEMS')
        urlopen.assert_called_with(url)
        self.assertEqual(info['title'], 'All Employees: Total Nonfarm Payrolls')
        self.assertEqual(info['frequency'], 'Monthly')
        self.assertEqual(info['frequency_short'], 'M')

    @mock.patch('fredapi.fred.urlopen')
    def test_invalid_id_in_get_series(self, urlopen):
        """Test invalid series id in get_series."""
        url = ('{}/series/observations?series_id=invalid&api_key={}'.
               format(self.root_url, fred_api_key))
        # some of the argument cannot be mocked easily.
        error = textwrap.dedent('''\
                <?xml version="1.0" encoding="utf-8" ?>
                <error code="400" message="Bad Request.
                The series does not exist." />\n\n\n\n
                ''')
        fp = io.StringIO(unicode(error))
        side_effect = fredapi.fred.HTTPError(url, 400, '', '', fp)
        self.prepare_urlopen(urlopen, side_effect=side_effect)
        with self.assertRaises(ValueError):
            self.fred.get_series('invalid')
        urlopen.assert_called_with(url)

    @mock.patch('fredapi.fred.urlopen')
    def test_invalid_id_in_get_series_info(self, urlopen):
        """Test invalid series id in get_series_info."""
        url = '{}/series?series_id=invalid&api_key={}'.format(self.root_url,
                                                              fred_api_key)
        error_msg = 'Bad Request.  The series does not exist.'
        # some of the argument cannot be mocked easily.
        xml_error = textwrap.dedent('''\
        <?xml version="1.0" encoding="utf-8" ?>
        <error code="400" message="{}" />\n\n\n
        '''.format(error_msg))
        fp = io.StringIO(unicode(xml_error))
        side_effect = fredapi.fred.HTTPError(url, 400, 'Bad Request', '', fp)
        self.prepare_urlopen(urlopen, side_effect = side_effect)
        with self.assertRaises(ValueError) as context:
            self.fred.get_series_info('invalid')
        self.assertEqual(unicode(context.exception), error_msg)
        urlopen.assert_called_with(url)

    @mock.patch('fredapi.fred.urlopen')
    def test_invalid_kwarg_in_get_series(self, urlopen):
        """Test invalid keyword argument in call to get_series."""
        url = '{}/series?series_id=invalid&api_key={}'.format(self.root_url,
                                                              fred_api_key)
        side_effect = fredapi.fred.HTTPError(url, 400, '', '', io.StringIO())
        self.prepare_urlopen(urlopen, side_effect=side_effect)
        # FIXME: different environment throw ValueError or TypeError.
        with self.assertRaises(Exception):
            self.fred.get_series('SP500', observation_start='invalid')
        self.assertFalse(urlopen.called)

    @mock.patch('fredapi.fred.urlopen')
    def test_search(self, urlopen):
        """Simple test to check retrieval of series info."""
        self.prepare_urlopen(urlopen, http_response=search_call.response)
        pi_series = self.fred.search_by_release(175, limit=3,
                                                order_by='series_id',
                                                sort_order='asc')
        urlopen.assert_called_with(search_call.url)
        actual = str(pi_series[['popularity', 'observation_start',
                                'seasonal_adjustment_short']])
        expected = textwrap.dedent('''\
                  popularity observation_start seasonal_adjustment_short
        series id                                                       
        PCPI01001          0        1969-01-01                       NSA
        PCPI01003          0        1969-01-01                       NSA
        PCPI01005          0        1969-01-01                       NSA''')
        self.assertEqual(actual.split('\n'), expected.split('\n'))

    @mock.patch('fredapi.fred.urlopen')
    def test_get_series_with_realtime(self, urlopen):
        """Test get_series with realtime argument."""
        side_effects = [gdp_obs_rt_call.response]
        self.prepare_urlopen(urlopen, side_effect=side_effects)
        df = self.fred.get_series('GDP', observation_start='7/1/2014',
                                  observation_end='1/1/2015',
                                  realtime_start='7/1/2014')
        urlopen.assert_called_with(gdp_obs_rt_call.url)
        actual = str(df)
        expected = textwrap.dedent('''\
                                                  GDP
            obs_date   rt_start   rt_end             
            2014-07-01 2014-10-30 2014-11-24  17535.4
                       2014-11-25 2014-12-22  17555.2
                       2014-12-23 NaT         17599.8
            2014-10-01 2015-01-30 2015-02-26  17710.7
                       2015-02-27 2015-03-26  17701.3
                       2015-03-27 NaT         17703.7
            2015-01-01 2015-04-29 2015-05-28  17710.0
                       2015-05-29 2015-06-23  17665.0
                       2015-06-24 NaT         17693.3''')
        self.assertEqual(actual.split('\n'), expected.split('\n'))

    @mock.patch('fredapi.fred.urlopen')
    def test_get_dataframe_forced_freq(self, urlopen):
        """Test get_dataframe to multi-series with heterogeous frequency."""
        series = ['SP500', 'GDP']
        side_effects = [sp500_obs_q_call.response,
                        gdp_obs_q_call.response]
        self.prepare_urlopen(urlopen, side_effect=side_effects)
        df = self.fred.get_dataframe(series, observation_start='7/1/2014',
                                     observation_end='1/1/2015',
                                     frequency='q')
        expected_calls = [(sp500_obs_q_call.url),
                          (gdp_obs_q_call.url)]
        for actual, expected in zip(urlopen.call_args_list, expected_calls):
            self.assertEqual(actual[0][0], expected)
        expected = textwrap.dedent('''\
                          SP500      GDP
            2014-07-01  1975.91  17599.8
            2014-10-01  2009.34  17703.7
            2015-01-01  2063.69  17693.3''')
        self.assertEqual(str(df), expected)

    @mock.patch('fredapi.fred.urlopen')
    def test_get_dataframe(self, urlopen):
        """Test get_dataframe to get multiple series with info."""
        series = ['GDP', 'PAYEMS']
        side_effects = [gdp_info_call.response,
                        gdp_obs_call.response,
                        payems_info_call.response,
                        payems_obs_call.response,]
        self.prepare_urlopen(urlopen, side_effect=side_effects)
        df = self.fred.get_dataframe(series, observation_start='7/1/2014',
                                     observation_end='1/1/2015')
        expected_calls = [(gdp_info_call.url),
                          (gdp_obs_call.url),
                          (payems_info_call.url),
                          (payems_obs_call.url)]
        for actual, expected in zip(urlopen.call_args_list, expected_calls):
            self.assertEqual(actual[0][0], expected)
        expected = textwrap.dedent('''\
                            GDP  PAYEMS
            2014-07-01  17599.8  139156
            2014-08-01      NaN  139369
            2014-09-01      NaN  139619
            2014-10-01  17703.7  139840
            2014-11-01      NaN  140263
            2014-12-01      NaN  140592
            2015-01-01  17693.3  140793''')

    @mock.patch('fredapi.fred.urlopen')
    def test_get_dataframe_with_realtime(self, urlopen):
        """Test get_dataframe to get multi-series with realtime info."""
        series = ['GDP', 'CP']
        side_effects = [gdp_info_call.response,
                        gdp_obs_rt_call.response,
                        cp_info_call.response,
                        cp_obs_rt_call.response,]
        self.prepare_urlopen(urlopen, side_effect=side_effects)
        df = self.fred.get_dataframe(series, observation_start='7/1/2014',
                                     observation_end='1/1/2015',
                                     realtime_start='7/1/2014')
        expected_calls = [(gdp_info_call.url),
                          (gdp_obs_rt_call.url),
                          (cp_info_call.url),
                          (cp_obs_rt_call.url)]
        for actual, expected in zip(urlopen.call_args_list, expected_calls):
            self.assertEqual(actual[0][0], expected)
        expected = textwrap.dedent('''\
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
        self.assertEqual(str(df), expected)

if __name__ == '__main__':
    unittest.main()
