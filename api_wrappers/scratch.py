# Third party imports
from ebaysdk.finding import Connection as Finding
import pandas

# Local imports
import config
from api_wrappers import ebay_api as ebay
from api_wrappers import data_analysis as data
from api_wrappers.errors import *

# Might want to make an ebay.yaml file and put API auth info in it
ebay_api = Finding(appid=config.ebay_app_id, config_file=None)


try:
    # resp = api.execute('findItemsAdvanced', {'keywords': 'Super Smash Bros', 'Condition': 'Used'})
    # resp = api.execute('findCompletedItems', {'keywords': 'Super Smash Bros', 'Condition': 'Used'})
    # results = _extract_results(resp)
    results = ebay.search_sold('Python for data analyis')
    cropped_data = data.get_stats(df=results, provider='ebay', asking_price=5)
    import pdb
    pdb.set_trace()
except ConnectionError as exc:
    print(exc)
