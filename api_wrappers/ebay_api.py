# Third party imports
from ebaysdk.finding import Connection as Finding
import pandas

# Local imports
import config
from api_wrappers.errors import *
from api_wrappers import utils

# Might want to make an ebay.yaml file and put API auth info in it
api = Finding(appid=config.ebay_app_id, config_file=None)

'''
A few notes to self:
    findItemsAdvanced only searches active listings and allows to search by keywords and narrow by category.
    findCompletedItems searches completed listings.
        BUT this includes both those items that sold AND those that ended without a sale. The 'sellingStatus'
            key within each item dict has a value which is also a dict. Within that there is a 'sellingState'
            field. To get only sold listings, need to filter by 'sellingState': 'EndedWithSales'. The opposite
            is 'EndedWithoutSales'. Other options are 'Canceled' or 'Ended'.
        Including 'sellingState': 'EndedWithSales' in the api.execute call DOES NOT WORK.

    Default number of return items is 100. Haven't looked into how to increase that.
    Need to check for isMultiVariationListing!! They are each listed separately and could skew averages. The
        Super Smash Bros search has ~20 of the 'same' result, just different variations.
'''


# THIS ONLY SEARCHES ACTIVE LISTINGS
def search_active(keywords):
    try:
        resp = api.execute('findItemsAdvanced', {'keywords': keywords, 'Condition': 'Used'})
    except ConnectionError:
        return None

    try:
        results = _extract_results(resp)
    except ZeroResultsException:
        results = None

    return results


def search_sold(keywords):
    """
    This method searches the completed items on eBay for the given keywords.
    Filters by only sold items.
    Only searches Used items.

    :param keywords: str, keywords for eBay search
    :return:
    """
    try:
        resp = api.execute('findCompletedItems', {'keywords': keywords, 'Condition': 'Used'})
    except ConnectionError:
        return None

    # Extract the list of results
    try:
        results = _extract_results(resp)
    except ZeroResultsException:
        return None

    # Filter by only those items that sold
    sold_items = []
    for item in results:
        # Try to get the sellingState of the item.
        # In case of an error (i.e. dict value does not exist), continue.
        try:
            sellingState = item['sellingStatus']['sellingState']
        except Exception:
            continue

        # If item sold, keep it
        if sellingState == 'EndedWithSales':
            sold_items.append(item)

    sold_items_df = _create_dataframe(sold_items)

    return sold_items_df


def _extract_results(response):
    if response is None:
        raise ConnectionError('No response from the server.')
    result_list = response.dict().get('searchResult')
    if result_list:
        results = result_list.get('item')
        if results:
            return results
    raise ZeroResultsException('No results found, or JSON was incorrectly parsed.')


def _create_dataframe(results):
    title = []
    is_multi_variation_listing = []
    category_id = []
    category_name = []
    sell_price = []
    shipping_type = []
    ship_price = []

    for result in results:
        ti, imvl, cid, cnm, sellp, shipt, shipp = _extract_json_fields(result)

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


def _extract_json_fields(result):
    # Navigates the multi-leveled JSON result produced by eBay
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

    return ti, imvl, cid, cnm, sellp, shipt, shipp
