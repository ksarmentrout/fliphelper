# Standard Imports

# Third party imports
from flask import Flask, render_template, request

from functions import data_analysis
from functions.api_wrappers import ebay_api as ebay
from functions.utils.errors import *

# Create the app
app = Flask(__name__)
app.config.from_object('flask_config')


# ---------------------------------------
# +++++++++++++++++++++++++++++++++++++++ Functions
# ---------------------------------------
def get_all_data(keywords, category, asking_price):
    """
    Based on the given category, this function queries the appropriate provider
    APIs, returns the data retrieved, and compiles them into a single dict,
    data_dict, which is returned.

    :param keywords:
    :param category:
    :param asking_price:
    :return:
    """
    data_dict = {}
    provider_count = 0

    # eBay stuff
    try:
        ebay_results_df = ebay.search_sold(keywords=keywords) # Get a dataframe of results from eBay
    except ZeroResultsException:
        ebay_data = {'results_df': None, 'count': 0, 'stats': None, 'provider': 'ebay'}
    else:
        stats = data_analysis.get_stats(df=ebay_results_df, provider='ebay', asking_price=asking_price)
        ebay_data = {'provider': 'ebay'}
        ebay_data.update(**stats)
    data_dict['ebay'] = ebay_data
    provider_count += 1

    data_dict['provider_count'] = provider_count
    return data_dict


# ---------------------------------------
# +++++++++++++++++++++++++++++++++++++++ Page serving
# ---------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/search_results', methods=['POST'])
def search_results():
    '''
    # Category will specify which of the various marketplaces to include.
    # For now, just focus on getting eBay running
    keywords = request.form['keywords']
    category = request.form['category']
    asking_price = request.form['asking_price']

    data_list = get_all_data(keywords=keywords, category=category, asking_price=asking_price)

    # Formatting
    asking_price = utils.to_float(asking_price)
    asking_price = '${:,.2f}'.format(asking_price)

    # var_dict = {'keywords': keywords, 'category': category, 'asking_price': asking_price, 'avg': stats['avg'],
    #             'median': stats['median'], 'std': stats['std'], 'verdict': stats['verdict'], 'count': count,
    #             'no_results': False}

    var_dict = {'keywords': keywords, 'category': category, 'asking_price': asking_price, 'data_list': data_list,
                'no_results': False}
    '''
    '''
    keywords = 'super smash bros melee'
    category = 'all'
    asking_price = '40'
    data_dict = get_all_data(keywords=keywords, category=category, asking_price=asking_price)
    data_dict['etsy'] = {'provider': 'etsy', 'verdict': 'pass',
                         'sold_stats': {'count': 200, 'avg': 65, 'median': 60, 'std': 8},
                         'active_stats': {'count': 201, 'avg': 75, 'median': 70, 'std': 16}
                         }
    data_dict['provider_count'] = 2

    '''
    data_dict = {'ebay':{'provider': 'ebay', 'verdict': 'pass',
                         'sold_stats': {'count': 100, 'avg': 50, 'median': 51, 'std': 12},
                         'active_stats': {'count': 101, 'avg': 60, 'median': 61, 'std': 15}
                         },
                 'etsy': {'provider': 'etsy', 'verdict': 'pass',
                          'sold_stats': {'count': 200, 'avg': 65, 'median': 60, 'std': 8},
                          'active_stats': {'count': 201, 'avg': 75, 'median': 70, 'std': 16}
                          },
                 'provider_count': 2}



    var_dict = {'keywords': 'hand-knitted backpacks', 'category': 'all', 'asking_price': 40, 'data_dict': data_dict,
                'no_results': False}
    return render_template('result_list.html', **var_dict)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/testing', methods=['GET'])
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False, host='0.0.0.0')
