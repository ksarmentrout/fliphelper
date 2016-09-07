# Standard imports
import os
import sys

import nose
import pandas

from functions import data_analysis
from functions.api_wrappers import ebay_api as ebay
from functions.utils.errors import *

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
        sys.path.insert(0, os.path.abspath('../functions'))

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
            numeric_df = df[['category_name', 'current_price']]

            # Check if there are any NaNs in them. Fail if so.
            if numeric_df.isnull().values.any():
                assert False
            else:
                assert True


# TODO: probably implement this such that it retrieves live data...
# As long as I don't change the function within data_analysis, it will
# never break if it keeps using the same saved data. The test will never fail
# if it keeps getting the same input, so it's not a useful test.
class TestDataAnalysis:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        active_filename = os.path.join(dir_path, 'ebay_active_results_df.csv')
        sold_filename = os.path.join(dir_path, 'ebay_sold_results_df.csv')

        self.ebay_active_df = pandas.read_csv(active_filename)
        self.ebay_sold_df = pandas.read_csv(sold_filename)

        self.asking_price = '40'

    def test_ebay_active_data_analysis(self):
        results_dict = data_analysis.get_stats(df=self.ebay_active_df, provider='ebay', asking_price=self.asking_price)

        # Assert that all of the returned values are numeric
        for key in results_dict.keys():
            if key == 'verdict':
                continue
            else:
                try:
                    float(results_dict.get(key))
                except Exception:
                    assert False
        pass

    # TODO: finish this
    def test_ebay_sold_data_analysis(self):
        results_dict = data_analysis.get_stats(df=self.ebay_sold_df, provider='ebay', asking_price=self.asking_price)
        pass


# Runs only nosetests from this module
if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__
    result = nose.run(argv=[sys.argv[0], module_name, '-v'])
