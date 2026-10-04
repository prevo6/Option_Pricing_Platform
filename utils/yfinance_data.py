import yfinance as yf
import numpy as np

def get_stock_data(symbol: str) -> list:
    """
    Fetches the "latest price" from yfinance and
    calculates the anualized volatility of the underlying asset 
    via downloading historical data, calculating the percentage change, taking 
    the standard deviation and multiplying by the sqrt of 252

    :param symbol: Valid yfinance ticker
    :type symbol: str
    :return: list containing latest price and annualized vol of the given asset
    :rtype: list
    """
    symbol = symbol.capitalize()

    ticker = yf.Ticker(symbol)
    latest_price = ticker.fast_info.last_price

    # try getting historical data 
    
    df = yf.download(symbol, start="2023-01-01", end="2026-01-01")

    # Use VIX ~15%
    if df.empty:
            annualized_vol = .15

    else: 
        returns = df["Close"].squeeze().pct_change().dropna()
        daily_vol = returns.std()
        annualized_vol = daily_vol * np.sqrt(252)

    return [latest_price, annualized_vol]

if __name__ == "__main__":
    # Test the function against multiple assets
    print(get_stock_data('SPX'))
    print(get_stock_data('GOOGL'))
    print(get_stock_data('SPY'))