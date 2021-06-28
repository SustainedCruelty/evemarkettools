import requests
import pandas as pd
import json
import bz2
import concurrent.futures
import os.path


def item_price(type_id: int, region_id: int = 10000002, system_id: int = None, order_type: str = 'sell'):
    """
    Pulls the market price for a specified type_id

    Args:
        type_id: type_id of the item to pull the price info for
        region_id: the region the orders should be pulled from. the default region_id is the Forge
        system_id: (optional) limits the orders to the systemID they were placed in
        order_type: specifies what information should be returned ('sell, 'buy' or 'all')

    Returns:
        float: returns the min sell or max buy as a float value (if order_type is set to 'buy' or 'sell')
        dict: returns the min sell and max buy in a dictionary as 'sell' and 'buy' (if order_type is set to 'all')
    """
    # Jita: 30000142, Amarr: 30002187, Hek: 30002053, Rens: 30002510, Dodixie: 30002659
    if order_type not in ['sell', 'buy', 'all']:
        raise ValueError("You didn't specify a valid order type ('sell','buy','all')")
    r = requests.get(
        f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type={order_type}&page=1&type_id={type_id}")
    orders = pd.DataFrame(r.json())
    pages = int(r.headers['X-Pages'])
    if pages > 1:
        for i in range(2, pages + 1):
            r = requests.get(f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility"
                             f"&order_type={order_type}&page={i}&type_id={type_id}").json()
            orders = orders.append(r, ignore_index=True)
    if system_id is not None:
        orders = orders.loc[orders['system_id'] == system_id]
    if order_type == 'sell':
        return orders['price'].min()
    if order_type == 'buy':
        return orders['price'].max()
    if order_type == 'all':
        return {'type_id': type_id,
                'buy': orders['price'].loc[(orders['is_buy_order'] == True)].max(),
                'sell': orders['price'].loc[(orders['is_buy_order'] == False)].min()}


def order_depth(type_id: int, region_id: int = 10000002, system_id: int = None, order_type: str = 'sell'):
    """
    Pulls the orders for a specified typeid in a region

    Args:
        type_id: typeid to pull the market orders for
        region_id: the region the orders should be pulled from. the default region_id is the Forge
        system_id: (optional) limits the orders to the systemID they were placed in
        order_type: specifies what orders should be returned ('sell, 'buy' or 'all')

    Returns:
        DataFrame: Returns a dataframe with the market orders
        NoneType: Returns None if the response is empty or the response code is anything other than 200
    """
    if order_type not in ['sell', 'buy', 'all']:
        raise ValueError("You didn't specify a valid order type ('sell','buy','all')")
    r = requests.get(
        f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type={order_type}&page=1&type_id={type_id}")
    if r.status_code != 200 or r.json() == []:
        return
    orders = pd.DataFrame(r.json())
    pages = int(r.headers['X-Pages'])
    if pages > 1:
        for i in range(2, pages + 1):
            r = requests.get(
                f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type={order_type}&page={i}&type_id={type_id}").json()
            orders = orders.append(r, ignore_index=True)
    if system_id is not None:
        orders = orders.loc[orders['system_id'] == system_id]
    if order_type == 'sell':
        return orders.sort_values('price', ascending=True).reset_index(drop=True)
    if order_type == 'buy':
        return orders.sort_values('price', ascending=False).reset_index(drop=True)
    return orders


def market_history(type_id: int, columns='all', region_id: int = 10000002, days: int = 400):
    """
    Pulls the market for a type_id in a region

    Args:
         type_id: return the market history for this item/ship
         columns: what data to return. take a string or list of strings. options are:
         'highest','lowest','average','order_count','volume','all'. Returns all columns by default
         region_id: returns the market history in this region
         days: pulls the market history for the last n days (1-400)

    Returns:
        returns a DataFrame with the market history. the oldest entry is at the top (index 0)
    """

    if isinstance(columns, list):
        columns = set(columns)
    else:
        columns = {columns}
    if not set(columns).issubset({'highest', 'lowest', 'average', 'order_count', 'volume', 'all'}):
        raise ValueError(
            "Those aren't valid columns. Supported types are: 'highest','lowest','average','order_count','volume','all'")
    if days <= 0:
        raise ValueError("'days' needs to be greater than zero and less than 400")
    r = requests.get(
        f"https://esi.evetech.net/latest/markets/{region_id}/history/?datasource=tranquility&type_id={type_id}")
    hist = pd.DataFrame(r.json())
    hist = hist.tail(days).reset_index(drop=True)
    if columns == {'all'} or 'all' in columns:
        return hist
    return hist[columns]


def item_quantity_price(type_id: int, quantity: int, region_id: int = 10000002, system_id: int = None,
                        order_type: str = 'sell'):
    """
        Calculates the isk needed to buy a specified quantity of an item considering order depth

        Args:
            type_id: type_id of the item to buy
            quantity: how much of the item to buy
            region_id: the region the orders should be pulled from. the default region_id is the Forge
            system_id: (optional) limits the market orders to a specific system
            order_type: select whether to sell to buy orders ('buy') or buy from sell orders ('sell')

        Returns:
            float: total buy/sell price
        """
    price, order = 0, 0
    orders = order_depth(type_id, region_id, system_id, order_type)
    if orders['volume_remain'].sum() < quantity:
        raise ValueError("Your order cannot be filled, choose a lower quantity or wider order range")
    while quantity > 0:
        if quantity <= orders['volume_remain'].iloc[order]:
            price += (quantity * orders['price'].iloc[order])
            return price
        elif quantity > orders['volume_remain'].iloc[order]:
            price += (orders['price'].iloc[order] * orders['volume_remain'].iloc[order])
            quantity -= orders['volume_remain'].iloc[order]
            order += 1


def structure_orders(refresh_token: str, structure_id: int = 1028858195912):
    """
        Pulls all market orders placed in a specified structure

        Args:
            refresh_token: valid refresh token to access the esi endpoint
            structure_id: structure to pull the orders from. default is set to the TTT

        Returns:
            DataFrame: returns a dataframe with all market orders from the specified citadel/structure
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic '
                         'Yjg5MmFiMThiNWU1NDMzM2E3ZWJmZTlhZGYzNjNkOTQ6Z0JmNWZ3YmttcUV0NWJjRjhlcE1GRk9IZXNDOEZaWDZMdng0RnpqWQ==',
    }
    data = '{"grant_type":"refresh_token", "refresh_token":%s}' % f'"{refresh_token}"'
    response = requests.post('https://login.eveonline.com/oauth/token', headers=headers, data=data)
    accesstoken = response.json()['access_token']

    url = f"https://esi.evetech.net/latest/markets/structures/{structure_id}/?datasource=tranquility"
    orders = pd.DataFrame()
    pages = int(authed_request(1, accesstoken, url).headers['X-Pages'])
    tokens, urls = [accesstoken] * pages, [url] * pages

    with concurrent.futures.ThreadPoolExecutor(max_workers=pages) as executor:
        results = executor.map(authed_request, list(range(1, pages + 1)), tokens, urls)
    for r in results:
        orders = orders.append(r.json(), ignore_index=True)

    return orders


def authed_request(page: int, access_token: str, url: str):
    """
        Makes an authenticated request to a specified URL

        Args:
            page: which page of results to return
            access_token: token needed to make the authenticated request
            url: url to pull the results from (without the &page parameter!)

        Returns:
            requests.Response: returns a response object created by making an authenticated request to the specified url
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = url + f"&page={page}"
    return requests.get(url, headers=headers)


def fuzz_static_dump(url='https://www.fuzzwork.co.uk/dump/latest/invTypes.csv.bz2'):
    """
    Downloads a csv from the fuzzworks static dump and converts it to a dataframe

    Args:
        url: fuzzwork url to download the csv from

    Returns:
        Dataframe containing the data from the downloaded csv.
    """
    comp_file = url.split('/')[-1]
    csv_file = comp_file.strip('.bz2')
    if not os.path.isfile(csv_file):
        r = requests.get(url)
        f = bz2.decompress(r.content)
        open(csv_file, 'wb').write(f)
    return pd.read_csv(csv_file)


def typeIDToName(typeID: int):
    if typeID not in invTypes['typeID'].values:
        raise ValueError("thats not a valid typeid")
    return invTypes['typeName'].loc[invTypes['typeID'] == typeID].iloc[0]


def typeNameToID(typeName: str):
    if typeName not in invTypes['typeName'].values:
        raise ValueError("thats not a valid typename")
    return invTypes['typeID'].loc[invTypes['typeName'] == typeName].iloc[0]


def typeIDToGroupID(typeID: int):
    if typeID not in invTypes['typeID'].values:
        raise ValueError("thats not a valid typeid")
    return invTypes['groupID'].loc[invTypes['typeID'] == typeID].iloc[0]


def groupIDToTypeID(groupID: int):
    if groupID not in invTypes['groupID'].values:
        raise ValueError("thats not a valid groupid")
    return list(invTypes['typeID'].loc[invTypes['groupID'] == groupID])


def regionNameToID(regionName: str):
    if regionName not in mapRegions['regionName'].values:
        raise ValueError("thats not a valid region name")
    return mapRegions['regionID'].loc[mapRegions['regionName'] == regionName].iloc[0]


def regionIDToName(regionID: int):
    if regionID not in mapRegions['regionID'].values:
        raise ValueError("thats not a valid region ID")
    return mapRegions['regionName'].loc[mapRegions['regionID'] == regionID].iloc[0]


def sysNameToID(sysName: str):
    if sysName not in mapSolarSystems['solarSystemName'].values:
        raise ValueError("thats not a valid system name")
    return mapSolarSystems['solarSystemID'].loc[(mapSolarSystems['solarSystemName'] == sysName)].iloc[0]


def sysIDToName(sysID: int):
    if sysID not in mapSolarSystems['solarSystemID'].values:
        raise ValueError("thats not a valid region name")
    return mapSolarSystems['solarSystemName'].loc[(mapSolarSystems['solarSystemID'] == sysID)].iloc[0]


def market_manipulation(typeID: int, margin: int = 1.5, capital: int = 10000000000):
    """
    Checks if an item is viable for market manipulation based on order depth

    Args:
         typeID: typeid of the item to check
         margin: minimum profit margin the market manipulation should yield
         capital: how much isk can be spent
    Return:
        returns a dictionary with the keys 'typeID', 'typeName', 'price', 'margin' and 'totalProfit' if the item is viable.
        Returns an empty dictionary if it's not.
    """
    orders = order_depth(typeID)
    isk_spent = 0
    items_bought = 0
    i = 0
    if orders is not None:
        while i < len(orders) - 1 and isk_spent < capital:
            items_bought += orders['volume_remain'].iloc[i]
            isk_spent += orders['price'].iloc[i] * orders['volume_remain'].iloc[i]
            m = (items_bought * orders['price'].iloc[i + 1]) / isk_spent
            totalProfit = (items_bought * orders['price'].iloc[i + 1]) - isk_spent
            if isk_spent < capital and m >= margin:
                return {'typeID': typeID,
                        'typeName': typeIDToName(typeID),
                        'price': orders['price'].iloc[i + 1],
                        'margin': m,
                        'totalProfit': totalProfit}
            i += 1
    return {}


def all_time_low(type_ids: list, timeframe: int = 400, region_id: int = 10000002, threshold: float = 1.0) -> dict:
    """
    Checks for a list typeids which items currently have the lowest average price in the last n days

    Args:
         type_ids: List or Series of type ids to check
         timeframe: how long to look back
         region_id: what region should the history be for
         threshold: lower the threshold for which an item is considered at an all time low.
         when comparing the current avg with the lowest avg in the specified timeframe, the lowest_avg is multiplied by the
         threshold to yield more items. default multiplier is 1.0 meaning current and lowest avg have to be equal.
    Returns:
        Return a dataframe with the columns: 'typeID', 'current_avg', 'lowest_avg', 'avg_volume'
    """
    res = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(type_ids), 400)) as executor:
        results = executor.map(price_hist_low, type_ids, [timeframe] * len(type_ids), [region_id] * len(type_ids))
    for r in results:
        print(f"Comparing {r['current_avg']} with {r['lowest_avg'] * threshold}")
        if r['current_avg'] <= (r['lowest_avg'] * threshold):
            res = res.append(r, ignore_index=True)
    return res


def price_hist_low(typeID: int, days: int, region_id: int):
    hist = market_history(typeID, region_id=region_id, days=days, columns=['average', 'volume'])
    return {'typeID': typeID,
            'current_avg': hist['average'][-1:].iloc[0],
            'lowest_avg': hist['average'].min(),
            'avg_volume': hist['volume'].mean()
            }

invTypes = fuzz_static_dump()
mapRegions = fuzz_static_dump('https://www.fuzzwork.co.uk/dump/latest/mapRegions.csv.bz2')
mapSolarSystems = fuzz_static_dump('https://www.fuzzwork.co.uk/dump/latest/mapSolarSystems.csv.bz2')
