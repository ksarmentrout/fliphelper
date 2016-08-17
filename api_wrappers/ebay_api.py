# Third party imports
from ebaysdk.finding import Connection as Finding

# Local imports
import config
from api_wrappers.errors import *

# Might want to make an ebay.yaml file and put API auth info in it
api = Finding(appid=config.app_id, config_file=None)

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
'''


# THIS ONLY SEARCHES ACTIVE LISTINGS
def search(keywords):
    try:
        resp = api.execute('findItemsAdvanced', {'keywords': keywords, 'Condition': 'Used'})
    except ConnectionError:
        return None

    results = extract_results(resp)


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
    results = extract_results(resp)

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

    return sold_items


def extract_results(response):
    if response is None:
        raise ConnectionError('No response from the server.')
    result_list = response.dict().get('searchResult')
    if result_list:
        results = result_list.get('item')
        if results:
            return results
    raise ZeroResultsException('No results found, or JSON was incorrectly parsed.')


try:
    # Might want to make an ebay.yaml file and put API auth info in it
    api = Finding(appid=config.app_id, config_file=None)
    # resp = api.execute('findItemsAdvanced', {'keywords': 'Python', 'Condition': 'Used'})
    resp = api.execute('findCompletedItems', {'keywords': 'Python', 'Condition': 'Used'})
    results = extract_results(resp)
    import pdb
    pdb.set_trace()
except ConnectionError as exc:
    print(exc)
