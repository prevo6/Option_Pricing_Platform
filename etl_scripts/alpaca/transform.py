import pandas as pd
import re
from datetime import datetime
from utils.yfinance_data import get_stock_data
from etl_scripts.alpaca.extract import fetch_from_alpaca

'python -m etl_scripts.alpaca.transform'

def _parse_occ_symbol(symbol: str) -> dict:

    """
    Helper function to take in the alpaca market options chain symbol and uses
    regex to parse info about the contract, including expiry, side, and strike price
    
    :param symbol: Alpaca Markets option contract chain symbol
    :type symbol: str
    :return: dict containing the expiry, side, and strike of the option contract
    :rtype: dict
    """

    match = re.match(r'^([A-Z]+)(\d{6})([CP])(\d{8})$', symbol)

    if match is None:
        raise ValueError(f"Not a valid OCC option symbol: {symbol!r}")
    
    
    underlying, exp, side, strike = match.groups()
    return {
        'underlying': underlying,
        'expiration': pd.to_datetime(exp, format='%y%m%d'),
        'side': 'call' if side == 'C' else 'put',
        'strike': int(strike) / 1000
    }

def clean_alpaca_data(alp_list: list) -> list[pd.DataFrame]:
    """
    Cleans alpaca JSON data into Postgres ready to load pandas dataframes 
    
    :param data: Alpaca options chain JSON data
    :type data: dict
    :return: Indexed list of pandas dataframes
        list[0]: underlying dataframe
        list[1]: option contract dataframe
        list[2]: quote dataframe

    :rtype: list[DataFrame]
    """
    data = alp_list[0]
    underlying_data = alp_list[1]

    und_df = pd.DataFrame()
    opt_df = pd.DataFrame()
    qte_df = pd.DataFrame()

    con_ids = list(data['snapshots'].keys())

    ids = []
    open_dates = []
    symbols = []
    expirys = []
    dtes = []
    strikes = []
    opt_types = []
    bids = []
    asks =[]
    last_prices = []
    volumes = []
    quote_timestamps = []


    # loops through the contracts and extracts contract info to be vectorized in Dataframes
    for key in con_ids:

        if 'dailyBar' not in data['snapshots'][key]:
            continue
        
        ids.append(key)
        parsed_data = _parse_occ_symbol(key)
        symbols.append(parsed_data['underlying'])
        expirys.append(parsed_data['expiration'])
        dtes.append((parsed_data['expiration'] - datetime.now()).days)
        opt_types.append(parsed_data['side'])
        strikes.append(parsed_data['strike'])
        open_dates.append(data['snapshots'][key]['dailyBar']['t'][:10])
        quote_timestamps.append(data['snapshots'][key]['latestQuote'].get('t').replace('T', ' ').replace('Z', ''))
        bids.append(data['snapshots'][key]['latestQuote'].get('bp'))
        asks.append(data['snapshots'][key]['latestQuote'].get('ap'))
        last_prices.append(data['snapshots'][key]['latestTrade'].get('p'))
        volumes.append(data['snapshots'][key]['dailyBar'].get('v'))



    opt_df['contract_id'] = ids
    opt_df['symbol'] = symbols
    opt_df['open_date'] = open_dates
    opt_df['open_date'] = opt_df['open_date'].astype(dtype='datetime64[ns]')
    opt_df['expiration_date'] = expirys
    opt_df['dte'] = dtes
    opt_df['strike_price'] = strikes
    opt_df['option_type'] = opt_types
    opt_df['multiplier'] = pd.Series([100] * len(con_ids))

    qte_df['contract_id'] = opt_df['contract_id']
    qte_df['timestamp'] = quote_timestamps
    qte_df['bid'] = bids
    qte_df['ask'] = asks
    qte_df['last_price'] = last_prices
    qte_df['volume'] = volumes
    qte_df['timestamp'] = qte_df['timestamp'].astype('datetime64[ns]')
    
    underlying_data = get_stock_data(opt_df['symbol'][0])
    und_df['symbol'] = [opt_df['symbol'][0]]
    und_df['last_price'] = [underlying_data[0]]
    und_df['updated_at'] = [datetime.now()]
    und_df['annualized_volatility'] = [underlying_data[1]]

    return [und_df, opt_df, qte_df]

if __name__ == "__main__":
    data = fetch_from_alpaca('SPX')
    clean_alpaca_data(data)
