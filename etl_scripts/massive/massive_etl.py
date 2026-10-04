from etl_scripts.massive.extract import fetch_from_massive
from etl_scripts.massive.transform import clean_massive_data
from etl_scripts.massive.load import load_massive
from database.connection import connect
import logging

def main() -> None:

    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    contracts = fetch_from_massive()
    dfs = clean_massive_data(contracts)
    load_massive(dfs, connect())


if __name__ == "__main__":
    main() #run the main script