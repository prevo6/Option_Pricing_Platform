import requests
import os
from dotenv import load_dotenv
from utils.yfinance_data import get_stock_data 


def fetch_from_alpaca(symbol: str) -> list:

    """
    Gets alpaca and yfinance data for the underlying ticker symbol
    
    :param symbol: Valid Alpaca & yFinance ticker
    :type symbol: str
    :return: list containing both alpaca json response and yfinance ticker data
        list[0]: Alpaca options chain JSON response
        list[1]: yfinance data containing spot price and annualized volatility
    :rtype: dict
    """

    url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{symbol}?feed=indicative&limit=1000"

    load_dotenv() 
    key = os.getenv("ALPACA_KEY")
    priv = os.getenv("ALPACA_SECRET")

    headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": key,
    "APCA-API-SECRET-KEY": priv
    }
    response = requests.get(url, headers=headers)

    underlying_data = get_stock_data(symbol)

    return [response.json(), underlying_data]

if __name__ == "__main__":
    print(fetch_from_alpaca())