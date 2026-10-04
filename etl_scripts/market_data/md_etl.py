from database.connection import connect
from etl_scripts.market_data.extract import fetch_from_md
from etl_scripts.market_data.transform import clean_md_options
from etl_scripts.market_data.load import load_from_md
import logging


def main() -> None:
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
    engine = connect()
    data = fetch_from_md()
    data = clean_md_options(data)
    load_from_md(data, engine)
    


if __name__ == "__main__":
    main()
    