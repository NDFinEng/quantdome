import mysql.connector
from mysql.connector.errors import IntegrityError
from datetime import datetime

from utils import timestamp_now
from utils.events import *
from utils.db import BaseStateStore

class MysqlHandler():
    """Class/context manager to connect to state store using mysql"""

    def __init__(self, db_name: str, sys_config: dict = None):
        self.db_name = db_name
        self.sys_config = sys_config
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.sys_config["mysql-config"]["host"],
                user=self.sys_config["mysql-config"]["user"],
                password=self.sys_config["mysql-config"]["password"],
                database=self.db_name
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to mysql database: {e}")
            raise e

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn is not None:
            try:
                self.conn.close()
                self.conn = None
                self.cursor = None
            except:
                pass

    def execute(self, expression: str, parameters: list = None, commit: bool = False):
        """Execute SQL expression"""
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(expression, parameters)
            if commit:
                self.conn.commit()
            return self.cursor
        except Exception as e:
            self.conn.rollback()
            raise e


    def insert_equities_historical(self, data: MarketUpdate):
        """Add historical data for a symbol"""

        try:
            self.execute(
                f"""INSERT INTO {self.sys_config["mysql-config"]["table_equities_historical"]} (
                    timestamp,
                    symbol,
                    high,
                    low,
                    open,
                    close,
                    volume
                )
                VALUES
                (%s, %s, %s, %s, %s, %s, %s)""",
                parameters=[
                    datetime.fromtimestamp(data.timestamp),
                    data.symbol,
                    data.high,
                    data.low,
                    data.open,
                    data.close,
                    data.volume,
                ],
                commit=True
            )
        except IntegrityError:
            print(f"Duplicate entry for {data.symbol} at {data.timestamp}")

    def insert_portfolio_state(self, data: PortfolioState):
        """Add portfolio state to log"""
        
        self.execute(
            f"""INSERT INTO {self.sys_config["mysql-config"]["table_portfolio_state"]} (
                timestamp,
                symbol,
                quantity,
                portfolio
            )
            VALUES
            (%s, %s, %s, %s)""",
            parameters=[
                datetime.fromtimestamp(data.timestamp),
                data.symbol,
                data.quantity,
                data.portfolio,
            ],
            commit=True
        )

    def insert_trade_signal(self, data: TradeSignal):
        """Add trade signal to log"""
        self.execute(
            f"""INSERT INTO {self.sys_config["mysql-config"]["table_trade_signals"]} (
                timestamp,
                symbol,
                price,
                quantity
            )
            VALUES
            (%s, %s, %s, %s)""",
            parameters=[
                datetime.fromtimestamp(data.timestamp),
                data.symbol,
                data.price,
                data.quantity,
            ],
            commit=True
        )

    def get_equities_historical(self, ticker: str):
        """Get historical data for a symbol"""

        self.execute(
            f"""SELECT * FROM {self.sys_config["mysql-config"]["table_equities_historical"]} WHERE symbol = %s""",
            parameters=[ticker]
        )

        return self.cursor.fetchall()