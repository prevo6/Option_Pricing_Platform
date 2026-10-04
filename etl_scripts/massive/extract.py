from massive import RESTClient
from dotenv import load_dotenv
import os
import logging
from massive.rest.models.contracts import OptionsContract


def fetch_from_massive() -> list[OptionsContract]:
    """
    This function most likely will fail early due to massive API limitations
    
    :return: OptionContract objects specific to the Massive API
    :rtype: list[OptionsContract]
    """
    logger = logging.getLogger(__name__)

    load_dotenv()
    key = os.getenv("MASSIVE_KEY")

    
    client = RESTClient(key)
    
    contracts = [] # store the options contract objects
    
    try:
    	for c in client.list_options_contracts(order="asc", limit=10, sort="ticker"):
         
         contracts.append(c)
         
    except:

        logger.warning("Fetching from Massive ended early")
        return contracts
    
    logger.info("Fully fetch Massive data")

    return contracts

if __name__ == "__main__":
    
	# test data for transform function
    data = fetch_from_massive()
    print(data)
 
