from sqlalchemy import Engine, text
from datetime import datetime
from database.connection import connect


def get_strikes(symbol: str, option_type: str , engine: Engine) -> list[float]:
    """
    Gets all strikes from db for specified ticker and option type (Call or Put)
    To be used to query user requests in app.py

    :param symbol: Ticker Symbol
    :type symbol: str
    :param option_type: Call or Put
    :type option_type: str
    :param engine: SqlAlchemy Engine
    :type engine: Engine
    :return: All strikes for that symbol + opt type
    :rtype: list[float]
    """
    with engine.begin() as con:

        res =con.execute(text(
            """
            SELECT strike_price FROM options_contracts
            WHERE symbol = :symbol AND option_type = :option_type
            AND expiration_date >= CURRENT_DATE;
            """
            
        )
        , {'symbol': symbol, 'option_type': option_type})
        rows = res.fetchall()

    return [row[0] for row in rows]


def get_expiries(symbol: str, option_type: str, strike_price: float, engine: Engine) -> list[datetime]:
    """
    Gets all available expiration dates from db given ticker, option type, and strike price.
    To be used internally in app.py for querying user requests
    
    :param symbol: Ticker Symbol for underlying
    :type symbol: str
    :param option_type: Call or Put
    :type option_type: str
    :param strike_price: Strike Price
    :type strike_price: int
    :param engine: SqlAlchemy Engine
    :type engine: Engine
    :return: List of all expirations *including expired 
    :rtype: list[datetime]
    """
    with engine.begin() as con:
        res = con.execute(text(
            """
            SELECT expiration_date FROM options_contracts
            WHERE symbol = :symbol AND option_type = :option_type 
            AND strike_price = :strike_price
            AND expiration_date >= CURRENT_DATE;

            """

        ), {'symbol': symbol, 'strike_price': strike_price, 'option_type': option_type}
        )
        rows = res.fetchall()
        return[row[0] for row in rows]


def get_underlyings(engine: Engine) -> list[str]:
    """
    Fetches all underlying asset ticker symbols from the database
    
    :param engine: sqlalchemy engine
    :type engine: Engine
    """

    with engine.begin() as con:

        res = con.execute(text(
            """
            SELECT symbol FROM underlying_assets;
            """

        ))

        rows = res.fetchall()
        return [row[0] for row in rows]


if __name__ == "__main__":
    
    engine = connect()
    strikes = get_strikes('SPX', 'call', engine)
    print(get_strikes('AMZN', 'call', engine))
    print(get_underlyings(engine))

    

    