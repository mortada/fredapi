"""  Created on 15/04/2024::
------------- test_with_proxies.py -------------
 
**Authors**: L. Mingarelli
"""
import os
import fredapi
PROXIES = {'http': 'xxx',
           'https': 'xxx'}

fred = fredapi.Fred(api_key=os.environ['FRED_API_KEY'], proxies=PROXIES)

data = fred.get_series('SP500')

