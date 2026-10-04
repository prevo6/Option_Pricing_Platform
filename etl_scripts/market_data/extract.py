from marketdata import MarketDataClient, MarketDataClientErrorResult
import os
from dotenv import load_dotenv
import logging
import pandas as pd
from utils.yfinance_data import get_stock_data

def fetch_from_md() -> list[pd.DataFrame, list] | None:
    
    """
    Fetches SPY Options Chain data from Market Data API

    returns:
        SPY options chain ataframe 
    """

    logger = logging.getLogger(__name__)

    load_dotenv() 
    key = os.getenv("MARKET_DATA_TOKEN")

    client = MarketDataClient(key)
    quotes = client.options.chain('SPY')
    if isinstance(quotes, MarketDataClientErrorResult):
        retry = 0
        for retry in range(1):
            quotes = client.options.chain('SPY')
        
        if isinstance(quotes, MarketDataClientErrorResult):
            logger.error(f"Market Data API Failure to Extract due to {quotes.error} ")
            return None
        else:
            logger.info(f"Market Data extraction complete took {retry} retries")
            return quotes
    else:
        logger.info("Market Data extraction complete first try")

        stock_data = get_stock_data('SPY')

        return [quotes, stock_data]



if __name__ == "__main__":
    df = fetch_from_md()
    print(df)
    
