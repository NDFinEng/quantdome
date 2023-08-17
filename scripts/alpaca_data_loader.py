from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest

from decouple import config

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from db_funcs import connect_database

ALPACA_KEY = config('ALPACA_KEY')
ALPACA_SECRET = config('ALPACA_SECRET')

def fetch_quotes_data(stock_ticker, start_date):
    client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)

    end_date = start_date + timedelta(hours=1)
    print(f'retrieving {stock_ticker} data for {start_date} to {end_date}')

    request_params = StockQuotesRequest(
        symbol_or_symbols=[stock_ticker],
        start=start_date,
        end=end_date
    )

    try:
        data = client.get_stock_quotes(request_params)
    except Exception as e:
        print(f'could not get data for {stock_ticker} at {start_date} to {end_date}')
        print(e)
        return {}
    
    
    if data is not None:
        data  = data.df.reset_index()
    else:
        print('no data returned')
        data = {}

    return data

def fetch_bars_data(stock_ticker, start_date):
    client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)

    end_date = start_date + timedelta(days=5)
    print(f'retrieving {stock_ticker} data for {start_date} to {end_date}')

    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Minute,
        start=start_date,
        end=end_date
    )

    try:
        data = client.get_stock_bars(request_params)
    except Exception as e:
        print(f'could not get data for {stock_ticker} at {start_date} to {end_date}')
        print(e)
        return {}
    
    if data is not None:
        data  = data.df.reset_index()
        print('data found!')
    else:
        print('no data returned')
        data = {}

    return data
    
def insert_quotes_row(row, db):
    cursor = db.cursor()
    try:

        insert_sql = """
        INSERT INTO quotes (symbol, timestamp, ask_exchange, ask_size, ask_price, bid_exchange, bid_size, bid_price, tape) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, row)
        db.commit()
    except Exception as e:
        print('error inserting row')
        print(e)
        db.commit()
        cursor.close()
        return -1
     
    cursor.close()
    return 0

def insert_bars_row(row, db):
    cursor = db.cursor()

    try:
        insert_sql = """
        INSERT INTO bars (symbol, timestamp, open, high, low, close, volume, trade_count, vwap) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, row)
        db.commit()
    except Exception as e:
        print('error inserting row')
        print(e)
        db.commit()
        cursor.close()
        return -1
    
    cursor.close()
    return 0
    
def save_to_db(data, db, count):
    #data.drop(labels='conditions', axis=1, inplace=True)
    for index, row in data.iterrows():
       if insert_bars_row(row, db) == 0:
           count += 1
       
    return count



def main():
    db = connect_database()
    if not db:
        return
    
    n_workers = 10

    # Connect database
    db = connect_database()

    stock_ticker = 'aapl'
    count = 0

    # Specify the start and end dates for fetching historical data
    start_date = datetime(2023, 6, 7)
    end_date = datetime(2023, 6, 30)

    # List to store the futures returned by ThreadPoolExecutor
    futures = []

    # Create ThreadPoolExecutor with the number of desired threads (e.g., 5)
    with ThreadPoolExecutor(max_workers=1) as executor:
        current_date = start_date
        while current_date < end_date:
            futures.append(executor.submit(fetch_bars_data, stock_ticker, current_date))
            current_date += timedelta(days=5)

    # Process the completed futures and save the data to the PostgreSQL database
    for future in as_completed(futures):
        data = future.result()
        if data is not None and not data.empty:
            count += save_to_db(data, db, count)

    print(f'Successfully inserted {count} rows')

if __name__ == "__main__":
    main()