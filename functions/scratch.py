# Third party imports

# Local imports

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
import os

from functions import data_analysis
from functions.api_wrappers import ebay_api as ebay

'''
Things to test:

eBay API:
    - Search sold returns either a populated df with numeric values, or throws an error. No df with NaN values.
    - ^ same for search active listings.
'''


keywords = 'skullcandy aviator headphones'
asking_price = '40'
category = 'all categories'


param_list = [
        ('super smash bros melee', '40'),  # This should give results
        ('Radiohead In Rainbows', '40'),  # This was originally returning NaN values
        ('faeronadjfnsaodfaeofihjkdzfabrauhfdajondfjaizxba', '40')  # This should return no results
    ]


# Getting all of the categories
'''
from ebaysdk.trading import Connection as Trading
import config
trading_api = Trading(appid=config.ebay_app_id, config_file=None, siteid='101')

callData = {
            'DetailLevel': 'ReturnAll',
            'CategorySiteID': 101,
            'LevelLimit': 4,
        }

# resp = trading_api.execute('GetCategories', callData)
'''


dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
file_dir = os.path.join(dir_path, 'tests')
active_filename = os.path.join(file_dir, 'ebay_active_results_df.csv')
sold_filename = os.path.join(file_dir, 'ebay_sold_results_df.csv')

active_df, count = ebay.search_active(keywords)
active_dict = data_analysis.get_stats(active_df, provider='ebay', asking_price='40')
print(active_dict)

sold_df, _ = ebay.search_sold(keywords)
sold_dict = data_analysis.get_stats(sold_df, provider='ebay', asking_price='40')
print(sold_dict)


# active_df.to_csv(active_filename)
# sold_df.to_csv(sold_filename)
