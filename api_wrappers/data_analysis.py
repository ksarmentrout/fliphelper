import pandas

from api_wrappers import utils


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

    price_avg = df['sell_price'].mean()
    price_std = df['sell_price'].std()

    # Set the high and low thresholds to be
    # average price +/- 2*std. This is so that
    # the titles of the outliers can be presented.

    # This may or may not be needed if we just instead
    # grab the top and bottom 5 or 10 items when ranked
    # by price.
    uthresh = price_avg + 2*price_std
    lthresh = price_avg - 2*price_std

    # Set the upper and lower bounds to be
    # average price +/- 3*std. This is so that
    # we drop the extreme outliers completely
    ubound = price_avg + 2.5*price_std
    lbound = price_avg - 2.5*price_std

    pruned_data = df.loc[lambda cutoff: (df.sell_price > lbound) & (df.sell_price < ubound), :]
    new_avg = pruned_data['sell_price'].mean()
    median = pruned_data['sell_price'].median()
    new_std = pruned_data['sell_price'].std()

    # TODO: sort pruned_data by price and retrieve the highest and lowest priced items

    if asking_price < (new_avg - .5*new_std):
        verdict = 'buy'
    else:
        verdict = 'pass'

    data_dict = {'avg': new_avg, 'median': median, 'std': new_std, 'verdict': verdict}

    return data_dict
