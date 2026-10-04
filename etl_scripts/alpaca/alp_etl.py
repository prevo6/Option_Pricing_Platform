from etl_scripts.alpaca.extract import fetch_from_alpaca
from etl_scripts.alpaca.transform import clean_alpaca_data
from etl_scripts.alpaca.load import load_alpaca
from database.connection import connect
from sqlalchemy import text
import logging

def main(symbol: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    engine = connect()
    data = fetch_from_alpaca(symbol)
    data = clean_alpaca_data(data)
    load_alpaca(data, engine)

def run_all_tracked_tickers() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    engine = connect()

    with engine.begin() as con:
        data = con.execute(text("SELECT * FROM alpaca_underlyings;"))
        rows = data.fetchall()
    list_of_unds = [row[1] for row in rows]

    for und in list_of_unds:
        try:
            main(und)
            logger.info(f"Ticker symbol: {und} updated to database")
        except Exception as e:
            logger.warning(f"Failed to load ticker symbol: {und} — {e}")

if __name__ == "__main__":
    run_all_tracked_tickers()