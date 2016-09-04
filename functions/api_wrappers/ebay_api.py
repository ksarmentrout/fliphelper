# Third party imports
import pandas
from ebaysdk.finding import Connection as Finding

import config
from functions.utils import utils
from functions.utils.errors import *

# Might want to make an ebay.yaml file and put API auth info in it
api = Finding(appid=config.ebay_app_id, config_file=None)

'''
A few notes to self:
    findItemsAdvanced only searches active listings and allows to search by keywords and narrow by category.
    findCompletedItems searches completed listings.

    The ship_price column isn't always a numeric value. If the shipping type is "Calculated", the ship_price
        column will be NaN.
'''


def search_active(keywords):
    """
    Searches eBay active listings for the provided keywords.
    :param keywords: User-entered string of keywords for the search.
    :return active_items_df: Pandas dataframe made by _create_active_dataframe()
    :return count: Integer number of results found/returned.
    """
    try:
        resp = api.execute('findItemsAdvanced', {'keywords': keywords})
    except ConnectionError:
        return None

    all_results = _extract_results(resp)

    # Determine how many pages of results there are
    pagination = resp.dict().get('paginationOutput')
    totalPages = pagination.get('totalPages')

    # Get 3 pages (or totalPages) of results
    limit = 3
    if totalPages is not None:
        if int(totalPages) < limit:
            limit = int(totalPages)

    for x in range(2, limit + 1):
        more_resp = api.execute('findCompletedItems', {'keywords': keywords, 'paginationInput': {'pageNumber': x}})
        more_results = _extract_results(more_resp)
        all_results.extend(more_results)

    count = len(all_results)
    active_items_df = _create_active_dataframe(all_results)

    return active_items_df, count


def search_sold(keywords):
    """
    This method searches the completed items on eBay for the given keywords.
    Filters by only sold items.
    Only searches Used items.

    :param keywords: str, keywords for eBay search
    :return:
    """
    try:
        # resp = api.execute('findCompletedItems', {'keywords': keywords, 'Condition': 'Used'})
        resp = api.execute('findCompletedItems', {'keywords': keywords, 'itemFilter': [{'name': 'SoldItemsOnly',
                                                  'value': True}]})
    except ConnectionError:
        return None

    # Extract the list of results
    # This will throw a ZeroResultsException if nothing is found.
    # That will be caught by master and used to render a different template.
    all_results = _extract_results(resp)

    # Determine how many pages of results there are
    pagination = resp.dict().get('paginationOutput')
    totalPages = pagination.get('totalPages')

    # Get 3 pages (or totalPages) of results
    limit = 3
    if totalPages is not None:
        if int(totalPages) < limit:
            limit = int(totalPages)

    for x in range(2,limit+1):
        more_resp = api.execute('findCompletedItems', {'keywords': keywords, 'paginationInput': {'pageNumber': x},
                                                       'itemFilter': [{'name': 'SoldItemsOnly', 'value': True}]})
        more_results = _extract_results(more_resp)
        all_results.extend(more_results)

    # This is no longer needed because I figured out how to properly use the itemFilter param
    '''
    # Filter by only those items that sold
    sold_items = []
    for item in all_results:
        # Try to get the sellingState of the item.
        # In case of an error (i.e. dict value does not exist), continue.
        try:
            sellingState = item['sellingStatus']['sellingState']
        except Exception:
            continue

        # If item sold, keep it
        if sellingState == 'EndedWithSales':
            sold_items.append(item)
    '''

    count = len(all_results)
    sold_items_df = _create_sold_dataframe(all_results)

    return sold_items_df, count


def _extract_results(response):
    """
    Navigates the JSON response to an API query.
    Determines if any results were found/returned, and if so,
    runs delete_multiples function and returns them.
    :param response: Direct JSON response from eBay API query.
    :return edited_results: List of results as dicts.
    """
    if response is None:
        raise ConnectionError('No response from the server.')
    result_list = response.dict().get('searchResult')
    if result_list:
        results = result_list.get('item')
        if results:
            edited_results = delete_multiples(results)
            return edited_results
    raise ZeroResultsException('No results were found.')


def delete_multiples(results):
    """
    Deletes the duplicated MultiVariationListings.
    If there is a listing on eBay that has multiple variations of the same thing
    (multiple colors of the same shirt, for example), they appear on eBay as different
    listings, but show up in the JSON as individual listings. If there are a lot of them,
    they could throw off the averages because they disproportionally weight a single
    sale price.
    Because there could be multiple sets of MultiVariationListings in a given set of
    100 results, I use the postal codes to distinguish between them.
    :param results: A list of JSON result dicts from an eBay API call.
    :return: A list of JSON result dicts without duplicates of the MultiVariationListings.
    """
    keep_indices = []
    postcodes = []
    for index, result in enumerate(results):
        # Check if it's a multiple
        if result.get('isMultiVariationListing') == 'true':
            # If the postcode hasn't already been recorded, it's the
            # first instance of a multiple for a given set of multiples.
            # Add its index to the 'keep' list.
            if result.get('postalCode') not in postcodes:
                postcodes.append(result.get('postalCode'))
                keep_indices.append(index)
        else:
            keep_indices.append(index)

    edited_results = [results[idx] for idx in keep_indices]
    return edited_results


def _create_sold_dataframe(results):
    """
    Creates a Pandas dataframe from the list of 'sold' results
    (i.e. the eBay listings that have ended and sold).
    :param results: List of dicts, which are individual eBay search results.
    :return df: Pandas dataframe with the relevant information extracted.
    """
    title = []
    is_multi_variation_listing = []
    category_id = []
    category_name = []
    sell_price = []
    shipping_type = []
    ship_price = []

    for result in results:
        ti, imvl, cid, cnm, sellp, shipt, shipp = _extract_json_fields(result, 'sold')

        title.append(ti)
        is_multi_variation_listing.append(imvl)
        category_id.append(cid)
        category_name.append(cnm)
        sell_price.append(sellp)
        shipping_type.append(shipt)
        ship_price.append(shipp)

    all_info_dict = {'title': title, 'is_multi_variation_listing': is_multi_variation_listing,
                     'category_id': category_id, 'category_name': category_name, 'sell_price': sell_price,
                     'shipping_type': shipping_type, 'ship_price': ship_price}

    df = pandas.DataFrame.from_dict(data=all_info_dict)
    return df


def _create_active_dataframe(results):
    """
    Creates a Pandas dataframe from the list of active results
    :param results: List of dicts, which are individual eBay search results.
    :return df: Pandas dataframe with the relevant information extracted.
    """
    title = []
    is_multi_variation_listing = []
    category_id = []
    category_name = []
    current_price = []
    is_buyitnow = []
    buyitnow_price = []
    shipping_type = []
    ship_price = []

    for result in results:
        ti, imvl, cid, cnm, curp, isbin, binp, shipt, shipp = _extract_json_fields(result, 'active')

        title.append(ti)
        is_multi_variation_listing.append(imvl)
        category_id.append(cid)
        category_name.append(cnm)
        current_price.append(curp)
        is_buyitnow.append(isbin)
        buyitnow_price.append(binp)
        shipping_type.append(shipt)
        ship_price.append(shipp)

    all_info_dict = {'title': title, 'is_multi_variation_listing': is_multi_variation_listing,
                     'category_id': category_id, 'category_name': category_name, 'current_price': current_price,
                     'is_buyitnow': is_buyitnow, 'buyitnow_price': buyitnow_price, 'shipping_type': shipping_type,
                     'ship_price': ship_price}

    df = pandas.DataFrame.from_dict(data=all_info_dict)
    return df


def _extract_json_fields(result, list_type):
    '''
    Navigates the multi-level JSON response from eBay for a single item result.
    :param result: JSON dict - response about one item from eBay
    :param list_type: str - either 'active' or 'sold', depending on which listings are queried
    :return: individual fields listed in _create_dataframe()
    '''
    ti = result.get('title')
    imvl = result.get('isMultiVariationListing')

    primary_category = result.get('primaryCategory')
    if primary_category is not None:
        cid = primary_category.get('categoryId')
        cnm = primary_category.get('categoryName')
    else:
        cid = None
        cnm = None

    # This next line is safe because items without a sellingStatus field
    # were filtered out in previous methods.
    current_price = result['sellingStatus'].get('currentPrice')
    if current_price is not None:
        sellp = utils.to_float(current_price.get('value'))
    else:
        sellp = None

    # Get fields specific to active listings
    if list_type == 'active':
        list_info = result['listingInfo']
        isbin = list_info['buyItNowAvailable']

        if isbin == 'true':
            binp = list_info['buyItNowPrice'].get('value')
            binp = utils.to_float(binp)
            if binp is None:
                binp = None
        else:
            binp = None


    shipping_info = result.get('shippingInfo')
    if shipping_info is not None:
        shipt = shipping_info.get('shippingType')
        service_cost = shipping_info.get('shippingServiceCost')
        if service_cost is not None:
            shipp = utils.to_float(service_cost.get('value'))
        else:
            shipp = None
    else:
        shipt = None
        shipp = None

    if list_type == 'active':
        return ti, imvl, cid, cnm, sellp, isbin, binp, shipt, shipp
    else:
        return ti, imvl, cid, cnm, sellp, shipt, shipp
