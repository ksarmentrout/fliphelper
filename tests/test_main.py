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


class TestEbay:
    def __init__(self):
        self.keywords = 'super smash bros melee'
        self.asking_price = '40'
        self.category = 'all categories'

        # Path management to appease py.test
        sys.path.insert(0, os.path.abspath('../api_wrappers'))

        self.param_list = [
                ('super smash bros melee', '40'),  # This should give results
                ('Radiohead In Rainbows', '40'),  # This was originally returning NaN values
                ('faeronadjfnsaodfaeofihjkdzfabrauhfdajondfjaizxba', '40')  # This should return no results
            ]

    def test_search_sold(self):
        for x in self.param_list:
            yield self.sold_helper, x[0], x[1]

    def test_search_active(self):
        for x in self.param_list:
            yield self.active_helper, x[0], x[1]

    def sold_helper(self, keywords, asking_price):
        try:
            df, count = ebay.search_sold(keywords)
        except ZeroResultsException:
            if keywords in ['super smash bros melee', 'Radiohead In Rainbows']:
                assert False
            else:
                assert True
        except Exception:
            assert False
        else:
            # Get only those columns from the df with numeric values
            numeric_df = df[['category_name', 'sell_price']]

            # Check if there are any NaNs in them. Fail if so.
            if numeric_df.isnull().values.any():
                assert False
            else:
                assert True

    def active_helper(self, keywords, asking_price):
        try:
            df, count = ebay.search_active(keywords)
        except ZeroResultsException:
            if keywords in ['super smash bros melee', 'Radiohead In Rainbows']:
                assert False
            else:
                assert True
        except Exception:
            assert False
        else:
            # Get only those columns from the df with numeric values
            numeric_df = df[['category_name', 'list_price']]

            # Check if there are any NaNs in them. Fail if so.
            if numeric_df.isnull().values.any():
                assert False
            else:
                assert True


# Runs only nosetests from this module
if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__
    result = nose.run(argv=[sys.argv[0], module_name, '-v'])
