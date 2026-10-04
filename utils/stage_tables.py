from sqlalchemy import Connection
import pandas as pd
import logging

def create_stage_tables(con: Connection, dfs: list[pd.DataFrame]) -> None:
    """
    Creates staging tables for easy loading into end user tables
    
    :param con: db connection
    :type con: Connection
    :param dfs: All dfs to be staged in database
    :type dfs: list[pd.DataFrame]
    """
    logger = logging.getLogger(__name__)

    dfs[0].to_sql(
        name='stage_underlying',
            con=con,
            if_exists='replace',
            index=False
            )

    dfs[1].to_sql(
            name='stage_options',
            con=con,
            if_exists='replace',
            index=False
            )
    
    try:
        dfs[2].to_sql(
            name='stage_quotes',
            con=con,
            if_exists='replace',
            index=False
            )
    except:
        logger.warning("Quotes Stage Table was not created")