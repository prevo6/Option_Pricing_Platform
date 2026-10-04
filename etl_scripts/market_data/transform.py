import pandas as pd
import logging

def clean_md_options(df: list[pd.DataFrame, list]) -> list[pd.DataFrame]:
    """
    Docstring for clean_md_options
   
    :param df: List of Market Data Options Dataframes 
    :type df: list[pd.DataFrame, list]
    :return: Cleaned market data dataframes to be appended to database
    :rtype: list[DataFrame]
    """
    
    logger = logging.getLogger(__name__)
    
    try:
        underlying_data = df[1]
        df = df[0]

        #moves optionSymbol from index to column
        df = df.reset_index()

        underlying_df = pd.DataFrame()
        options_df = pd.DataFrame()
        quotes_df = pd.DataFrame()

        underlying_df['symbol'] = df['underlying']
        underlying_df['last_price'] = df['underlyingPrice']
        underlying_df['updated_at'] = df['updated']
        

        underlying_df = underlying_df.drop_duplicates(subset='symbol', keep='last')
        underlying_df['annualized_volatility'] = [underlying_data[1]]

        options_df['contract_id'] = df['optionSymbol']
        options_df['symbol'] = df['underlying']
        options_df['open_date'] = df['firstTraded']
        options_df['expiration_date'] = df['expiration']
        options_df['dte'] = df['dte']
        options_df['strike_price'] = df['strike']
        options_df['option_type'] = df['side']
        options_df['multiplier'] = pd.Series([100] * len(df))
  
        quotes_df['contract_id'] = df['optionSymbol']
        quotes_df['timestamp'] = df['updated']
        quotes_df['bid'] = df['bid']
        quotes_df['ask'] = df['ask']
        quotes_df['last_price'] = df['last']
        quotes_df['volume'] = df['volume']
        quotes_df['open_interest'] = df['openInterest']
        quotes_df['implied_volatility'] = df['iv']
        quotes_df['delta'] = df['delta']
        quotes_df['gamma'] = df['gamma']
        quotes_df['theta'] = df['theta']
        quotes_df['vega'] = df['vega']

        return [underlying_df, options_df, quotes_df]
    
    except Exception as e:
        logger.error(f"Error in creating Market Data Dataframes due to {e}")
        raise

    