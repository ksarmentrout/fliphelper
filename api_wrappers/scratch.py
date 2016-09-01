# Third party imports
from ebaysdk.finding import Connection as Finding
import pandas

# Local imports
import config
from api_wrappers import ebay_api as ebay
from api_wrappers import data_analysis as data
from api_wrappers.errors import *

# Might want to make an ebay.yaml file and put API auth info in it
# ebay_api = Finding(appid=config.ebay_app_id, config_file=None)

'''
try:
    results = ebay.search_sold('Python for data analyis')
    cropped_data = data.get_stats(df=results, provider='ebay', asking_price=5)
    import pdb
    pdb.set_trace()
except ConnectionError as exc:
    print(exc)
'''

# Standard imports
import sys
import os

# Third-party imports
import pandas
import nose

# Local imports
from api_wrappers import ebay_api as ebay
from api_wrappers.errors import *

'''
Things to test:

eBay API:
    - Search sold returns either a populated df with numeric values, or throws an error. No df with NaN values.
    - ^ same for search active listings.
'''


keywords = 'Radiohead In Rainbows'
asking_price = '40'
category = 'all categories'

# Path management to appease py.test
sys.path.insert(0, os.path.abspath('../api_wrappers'))

param_list = [
        ('super smash bros melee', '40'),  # This should give results
        ('Radiohead In Rainbows', '40'),  # This was originally returning NaN values
        ('faeronadjfnsaodfaeofihjkdzfabrauhfdajondfjaizxba', '40')  # This should return no results
    ]

df, count = ebay.search_sold(keywords)
# Get only those columns from the df with numeric values
numeric_df = df[['category_name', 'sell_price']]

# Check if there are any NaNs in them. Fail if so.
if numeric_df.isnull().values.any():
    print('NaN found')
else:
    print("It's all good")


