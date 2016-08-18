# Standard Imports
import os

# Third party imports
from flask import Flask, render_template, request

# Local imports
from api_wrappers import ebay_api as ebay
from api_wrappers import data_analysis

# Create the app
app = Flask(__name__)
app.config.from_object('flask_config')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    # Category will specify which of the various marketplaces to include.
    # For now, just focus on getting eBay running
    keywords = request.form['keywords']
    category = request.form['category']
    asking_price = request.form['asking_price']
    ebay_results_df = ebay.search_sold(keywords=keywords) # Get a dataframe of results from eBay
    stats = data_analysis.get_stats(df=ebay_results_df, provider='ebay', asking_price=asking_price)

    var_dict = {'keywords': keywords, 'category': category, 'asking_price': asking_price, 'avg': stats['avg'],
                'median': stats['median'], 'std': stats['std'], 'verdict': stats['verdict']}

    return render_template('result_list.html', **var_dict)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')
