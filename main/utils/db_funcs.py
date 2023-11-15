from decouple import config

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

USER     = 'peter'
PASSWORD = config('DB_PASS')
URL = f'postgresql://{USER}:{PASSWORD}@quantdome-12092.5xj.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full'


def connect_database():
    try:
        conn =  psycopg2.connect(URL,
                            cursor_factory=psycopg2.extras.RealDictCursor)
        print('database connection successful')
        return conn
    except Exception as e:
        print('database connection failed')
        print(e)
        return

def create_quotes_table():

    db = connect_database()

    query = """
    CREATE TABLE quotes (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    ask_exchange VARCHAR(10),
    ask_size FLOAT NOT NULL,
    ask_price FLOAT NOT NULL,
    bid_exchange VARCHAR(10),
    bid_size FLOAT NOT NULL,
    bid_price FLOAT NOT NULL,
    tape VARCHAR(10),
    PRIMARY KEY(symbol, timestamp)
    );
    """
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
        print("quotes table creation successful")
        cursor.close()
        
    except Exception as e:
        print("quotes table creation failed")
        print(e)
        cursor.close()
        return -1
    
    return 0

def create_bars_table():

    db = connect_database()

    query = """
    CREATE TABLE bars (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    trade_count INTEGER NOT NULL,
    vwap FLOAT NOT NULL,
    PRIMARY KEY(symbol, timestamp)
    );
    """

    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
        print("bars table creation successful")
        cursor.close()
        
    except Exception as e:
        print("quotes table creation failed")
        print(e)
        cursor.close()
        return -1
    
    return 0


# WARNING: THINK REALLY HARD BEFORE RUNNING THIS
def delete_table(tblname):
    db = connect_database()
    query=f"""
    DROP TABLE {tblname}
    """
    cursor = db.cursor()

    try:
        cursor.execute(query)
        db.commit()
        print(f"{tblname} table deletion successful")
        cursor.close()

    except Exception as e:
        print(f'could not delete table {tblname}')
        print(e)
        return -1
    
    return 0