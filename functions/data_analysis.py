# Third party imports
import pandas

# Local imports
from functions.utils import utils
from functions.utils.errors import *


def get_stats(df, provider, asking_price):
    if provider == 'ebay':
        return ebay_analysis(df, asking_price)
    else:
        return None


def ebay_analysis(df, asking_price):
    '''
    df columns:
        title
        is_multi_variation_listing
        category_id
        category_name
        sell_price
        shipping_type
        ship_price

    :param df: pandas dataframe
    '''
    asking_price = utils.to_float(asking_price)

    # Check if the df is for active or sold listings
    is_sold_data = False
    is_active_data = False
    if df['data_type'][0] == 'active':
        is_active_data = True
    else:
        is_sold_data = True

    if is_active_data:
        going_prices = df['current_price']
        bin_prices = df['buyitnow_price']
        bin_prices = bin_prices.dropna()  # Drops the NaN values
        is_active_data = True
    else:
        going_prices = df['sell_price']
        is_sold_data = True

    price_avg = going_prices.mean()
    price_std = going_prices.std()

    # Set the high and low thresholds to be
    # average price +/- 2*std. This is so that
    # the titles of the outliers can be presented.

    # This may or may not be needed if we just instead
    # grab the top and bottom 5 or 10 items when ranked
    # by price.
    # uthresh = price_avg + 2*price_std
    # lthresh = price_avg - 2*price_std

    # Set the upper and lower bounds to be
    # average price +/- std. This is so that
    # we drop the extreme outliers completely
    ubound = price_avg + price_std
    lbound = price_avg - price_std

    pruned_data = going_prices.loc[lambda cutoff: (going_prices > lbound) & (going_prices < ubound)]
    new_avg = pruned_data.mean()
    median = pruned_data.median()
    new_std = pruned_data.std()

    if is_active_data:
        pruned_bin_data = bin_prices.loc[lambda cutoff: (bin_prices > lbound) &
                                                        (bin_prices < ubound)]
        bin_avg = pruned_bin_data.mean()
        bin_median = pruned_bin_data.median()
        bin_std = pruned_bin_data.std()
        plot_data = None
    else:
        bin_avg = None
        bin_median = None
        bin_std = None
        dates, mean_values = get_ebay_sold_plot_data(df)
        plot_data = {'dates': dates, 'mean_values': mean_values}


    # TODO: sort pruned_data by price and retrieve the highest and lowest priced items

    if asking_price < (new_avg - .5*new_std):
        verdict = 'buy'
    else:
        verdict = 'pass'

    # Create data_dict
    data_dict = {'verdict': verdict, 'plot_data': plot_data}

    # Give the stats monetary formatting
    stats_dict = {'avg': new_avg, 'median': median, 'std': new_std,
                  'bin_avg': bin_avg, 'bin_median': bin_median, 'bin_std': bin_std,
                  'count': len(df)}

    # Formatting:
    for x in ['avg', 'median', 'std', 'bin_avg', 'bin_median', 'bin_std']:
        if stats_dict.get(x) is not None:
            stats_dict[x] = '${:,.2f}'.format(stats_dict[x])

    if is_active_data:
        data_dict['active_stats'] = stats_dict
    else:
        data_dict['sold_stats'] = stats_dict

    return data_dict


def get_ebay_sold_plot_data(df):
    sdf = df.groupby([df.end_time.dt.week, df.end_time.dt.year])
    avgs = sdf.mean()

    # Extract data into lists for use with Chart.js
    # Dates is a list of (week, year) tuples
    dates = []
    for x in sdf.groups:
        dates.append(x)
    date_labels = ['Week ' + str(x[0]) + ', ' + str(x[1]) for x in dates]

    mean_values = avgs['sell_price'].tolist()

    return date_labels, mean_values
