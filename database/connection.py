import psycopg
from sqlalchemy import create_engine, Engine
import os
from dotenv import load_dotenv


def connect() -> Engine:
    load_dotenv()

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")

    url = f"postgresql+psycopg://{user}:{password}@{host}/{database}"
  
    engine = create_engine(
        url,
        pool_pre_ping=True  
    )

    return engine
    

if __name__ == "__main__":
    en = connect()
    with en.connect() as con:
        print(con)
        

    
