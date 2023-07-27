from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest
from decouple import config
import mysql.connector

from abc import ABCMeta, abstractmethod
import datetime

HOSTNAME = 'quantdome-db.cmcwk2c3qq7c.us-east-2.rds.amazonaws.com'
PORT     = '3306'
USER     = 'admin'
PASSWORD = config('DB_PASS')
DATABASE = 'quantdome'

def connect_database():
    return mysql.connector.connect(
        host=HOSTNAME,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

def print_tables(db):
    cursor = db.cursor()
    cursor.execute('desc quotes;')
    for table in cursor:
        print(table)

def main():
    db = connect_database()
    print_tables(db)

if __name__ == "__main__":
    main()