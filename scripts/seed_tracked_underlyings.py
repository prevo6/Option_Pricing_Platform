from database.connection import connect
import requests
import os
from dotenv import load_dotenv
import pandas as pd


# Helper script to track underlying tickers primarly for alpaca markets


def dump_alpaca_tickers() -> pd.DataFrame:
    """
    Connects to alpaca markets to get all available tickers saves them in a DataFrame
    
    :return: All available tickers from alpaca 
    :rtype: DataFrame
    """
    df = pd.DataFrame()
    list_of_unds = []

    load_dotenv()

    key = os.getenv("ALPACA_KEY")
    priv = os.getenv("ALPACA_SECRET")

    url = "https://paper-api.alpaca.markets/v2/assets"

    headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": key,
    "APCA-API-SECRET-KEY": priv,
    }

    response = requests.get(url, headers=headers)
    json_obj = response.json()

    for und in json_obj:
        if 'has_options' in und['attributes']:
            list_of_unds.append(und['symbol'])

    df['underlying'] = list_of_unds

    return df


def seed_tickers(df: pd.DataFrame) -> None:
    """
    Updates or creates all the tickers in the database to be used by the alpaca pipeline
    
    :param df: Dataframe of tickers
    :type df: pd.DataFrame
    """
    engine = connect()

    with engine.begin() as con:
        df.to_sql(
            name='alpaca_underlyings',
            con=con,
            if_exists="replace"
        )
    
if __name__ == "__main__":

    # add the underlyings to the table (ran once upon project spin up)
    df = dump_alpaca_tickers()
    seed_tickers(df)