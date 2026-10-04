from massive.rest.models.contracts import OptionsContract
import pandas as pd
from utils.yfinance_data import get_stock_data
from datetime import datetime
from extract import fetch_from_massive
import logging

def clean_massive_data(contracts: list[OptionsContract]) -> list[pd.DataFrame]:
    
    """
    Returns formatted Dataframes for easy database insertion. Excludes Quotes df due
    to Massive API limitations
    
    :param contracts: List of Massive API contract objects
    :type contracts: list[OptionsContract]
    :return: list[0]: underlying_df
             list[1]: option_df
    :rtype: list[DataFrame]
    """

    logger = logging.getLogger(__name__)

    und_df = pd.DataFrame()
    opt_df = pd.DataFrame()

    #staging lists
    und_tickers = []
    last_prices = []
    updated_at = []
    vols = []
    c_ids = []
    expirys = []
    strikes = []
    opt_types = []
    multipliers = []

    # gets the underlying ticker and volatility for the first contract to reduce API calls

    try:
        yfinance_data = get_stock_data(contracts[0].underlying_ticker)
        underlying_data = [contracts[0].underlying_ticker , yfinance_data[0], yfinance_data[1]]

    except:
        logger.warning("Underlying spot and volatility failed from yfinance")
        underlying_data = [None, None] # prevent list index exception

    for c in contracts:

        und_tickers.append(c.underlying_ticker)

        try:

            # check if the first underlying ticker equals the current one
            if underlying_data[0] != c.underlying_ticker:
            
                new_und_data = get_stock_data(c.underlying_ticker)
                last_prices.append(new_und_data[0])
                vols.append(new_und_data[1])

            # otherwise use the same ticker and volatility
            else:
                last_prices.append(underlying_data[1])
                vols.append(underlying_data[2])

        except:
            logger.error(f"""Lastest Price for underlying {c.underlying_ticker} failed to extract from
                         Massive Data API. Null value appended to database!
                         """)
            last_prices.append(None)

        updated_at.append(datetime.now())
        c_ids.append(c.ticker)
        expirys.append(c.expiration_date)
        strikes.append(c.strike_price)
        opt_types.append(c.contract_type)
        multipliers.append(c.shares_per_contract)

    und_df['symbol'] = und_tickers
    und_df['last_price'] = last_prices
    und_df['updated_at'] = updated_at
    und_df['annualized_volatility'] = vols

    und_df = (
    und_df
    .sort_values('updated_at')
    .drop_duplicates(subset='symbol', keep='last')
    )

    opt_df['contract_id'] = c_ids
    opt_df['symbol'] = und_tickers
    opt_df['open_date'] = pd.Series([pd.NaT] * len(opt_df), dtype='datetime64[ns]')
    opt_df['expiration_date'] = pd.Series(expirys, dtype='datetime64[ns]')
    opt_df['dte'] = pd.Series([pd.NA] * len(opt_df), dtype='Int64') 
    opt_df['strike_price'] = strikes
    opt_df['option_type'] = opt_types
    opt_df['multiplier'] = multipliers

    return [und_df, opt_df]


if __name__ == "__main__":

    """
    contracts = fetch_from_massive()
    print(contracts[0].underlying_ticker is contracts[1].underlying_ticker)

    """

    data = fetch_from_massive()
    cleaned_data = clean_massive_data(data)
    print(cleaned_data[0])

    print()

    print(cleaned_data[1])
