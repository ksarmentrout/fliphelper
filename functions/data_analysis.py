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

    is_sold_data = False
    is_active_data = False

    # Check if the df is for active or sold listings
    # If there is no 'sell_price' category, the df is
    # for active listings
    try:
        going_prices = df['sell_price']
        is_sold_data = True
    except KeyError:
        going_prices = df['current_price']
        bin_prices = df['buyitnow_price']
        bin_prices = bin_prices.dropna()  # Drops the NaN values
        is_active_data = True

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
    elif is_sold_data:
        bin_avg = None
        bin_median = None
        bin_std = None
    else:
        raise DataFrameError('Dataframe not identified as either active or sold.')

    # TODO: sort pruned_data by price and retrieve the highest and lowest priced items

    if asking_price < (new_avg - .5*new_std):
        verdict = 'buy'
    else:
        verdict = 'pass'

    data_dict = {'avg': new_avg, 'median': median, 'std': new_std, 'verdict': verdict,
                 'bin_avg': bin_avg, 'bin_median': bin_median, 'bin_std': bin_std}

    # Formatting:
    for x in ['avg', 'median', 'std', 'bin_avg', 'bin_median', 'bin_std']:
        if data_dict.get(x) is not None:
            data_dict[x] = '${:,.2f}'.format(data_dict[x])

    return data_dict
