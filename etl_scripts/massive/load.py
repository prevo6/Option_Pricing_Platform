import pandas as pd
from sqlalchemy import Engine, text
from utils.stage_tables import create_stage_tables
import logging
from etl_scripts.massive.extract import fetch_from_massive
from etl_scripts.massive.transform import clean_massive_data
from database.connection import connect

def load_massive(data: list[pd.DataFrame], engine: Engine) -> None:
    """
    Loads massive data into postgres
    
    :param data: List containing 2 dataframes 
                    data[0]: underlying df, 
                    data[1]: options df

    :type data: list[pd.DataFrame]
    :param engine: sqlalchemy engine object from established connection
    :type engine: Engine
    """

    logger = logging.getLogger(__name__)
    try:
        with engine.begin() as con:

            create_stage_tables(con, data)

            logger.info("Stage table created for Massive market data")


            con.execute(text("""INSERT INTO underlying_assets(symbol, last_price, updated_at, annualized_volatility)
                    SELECT symbol, last_price, updated_at , annualized_volatility
                    FROM stage_underlying
                    ON CONFLICT (symbol)
                    DO UPDATE SET last_price = EXCLUDED.last_price, updated_at = EXCLUDED.updated_at, annualized_volatility = EXCLUDED.annualized_volatility;
                 """))
        

            logger.info("Underlying data added from Massive API")

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

            logger.info("Options contract data added from Massive API")

    except Exception as e:
        logger.error(f"Loading Massive data failed due to Exception: {e}")


if __name__ == "__main__":

    contracts = fetch_from_massive()
    dfs = clean_massive_data(contracts)
    load_massive(dfs, connect())