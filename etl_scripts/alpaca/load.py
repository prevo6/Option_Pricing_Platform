import pandas as pd
import logging
from sqlalchemy import Engine, text
from utils.stage_tables import create_stage_tables

def load_alpaca(data: list[pd.DataFrame], engine: Engine) -> None:

    """
    Loads list of pandas dataframes into PostreSQL staging tables
    Upserts staging tables into PostgreSQL main tables
    
    :param dfs: list of pandas dataframes for staging
    :type dfs: list[pd.DataFrame]
    :param engine: SQLalchemy engine for connection
    :type engine: Engine
    """
    logger = logging.getLogger(__name__)


    try:
        
        with engine.begin() as con:

            # STAGING TABLES
            create_stage_tables(con, data)

            logger.info('Stage Tables Created')


            # inserts the new underlying asset if it doesn't exist otherwise updates the price and date updated
            con.execute(text("""INSERT INTO underlying_assets(symbol, last_price, updated_at, annualized_volatility)
                    SELECT symbol, last_price, updated_at, annualized_volatility 
                    FROM stage_underlying
                    ON CONFLICT (symbol)
                    DO UPDATE SET last_price = EXCLUDED.last_price, updated_at = EXCLUDED.updated_at, annualized_volatility = EXCLUDED.annualized_volatility;
                 """))

            # inserts new option contract data or updates dte if contract already exists in database
            con.execute(text(
            """
            INSERT INTO options_contracts(contract_id, symbol, open_date,
            expiration_date, dte, strike_price, option_type, multiplier)
            SELECT contract_id, symbol, open_date, expiration_date, dte, strike_price, option_type, multiplier
            FROM stage_options
            ON CONFLICT (contract_id)
            DO UPDATE SET dte = EXCLUDED.dte;
            """
            ))

            # append the quote data to the table history
            con.execute(text(
            """ 
            INSERT INTO options_quote_history(
            contract_id, timestamp, bid, ask, last_price, volume
            )
            SELECT contract_id, timestamp, bid, ask, last_price, volume
            FROM stage_quotes;
            """

            ))

        logger.info(f'Alpaca Markets Data appended to Database for ticker {data[0]['symbol']}')

    except Exception as e:
        logger.error(f"Loading Alpaca market data failed due to {e}")