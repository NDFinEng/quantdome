# test mysql db module
import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.db.mysql import MysqlHandler
from utils import (
    get_script_name,
    get_hostname,
    log_ini,
    get_system_config,
    validate_cli_args,
    timestamp_now,
)

from utils.events import *

SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

def test_db_connection():
    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        assert db.conn is not None
        assert db.cursor is not None

    assert db.conn is None
    assert db.cursor is None

    print("Mysql DB Connection Test Passed!")

def test_db_insert_equities_historical():
    
    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        # create market update object
        market_update = MarketUpdate(
            symbol='AAPL',
            timestamp=timestamp_now(),
            high=100,
            low=50,
            open=75,
            close=75,
            volume=1000,
        )

        # insert market update
        db.insert_equities_historical(market_update)

        # check if inserted
        db.cursor.execute(
            f"""SELECT * FROM equities_historical 
                WHERE symbol=%s 
                AND timestamp=%s""", 
            (
                market_update.symbol, 
                market_update.timestamp
            )
        )
        result = db.cursor.fetchone()

        assert result is not None
        assert result[1] == 'AAPL'
        assert result[2] == 100
        assert result[3] == 50
        assert result[4] == 75
        assert result[5] == 75
        assert result[6] == 1000

        # delete inserted row
        db.cursor.execute(
            f"""DELETE FROM equities_historical 
                WHERE symbol=%s 
                AND timestamp=%s""",
            (
                market_update.symbol, 
                market_update.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        db.conn.commit()

        print("Mysql DB Insert Equities Historical Test Passed!")

def test_db_insert_portfolio_state():

    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        # create portfolio state object
        portfolio_state = PortfolioState(
            timestamp=timestamp_now(),
            symbol='AAPL',
            value=100,
            quantity=10,
            portfolio='test'
        )

        # insert portfolio state
        db.insert_portfolio_state(portfolio_state)

        # check if inserted
        db.cursor.execute(
            f"""SELECT * FROM portfolio_state 
                WHERE symbol=%s 
                AND timestamp=%s""", 
            (
                portfolio_state.symbol, 
                portfolio_state.timestamp
            )
        )
        result = db.cursor.fetchone()

        assert result is not None
        assert result[1] == 'AAPL'
        assert result[2] == 10
        assert result[3] == 100
        assert result[4] == 10 * 100
        assert result[5] == 'test'



        # delete inserted row
        db.cursor.execute(
            f"""DELETE FROM portfolio_state 
                WHERE symbol=%s 
                AND timestamp=%s""",
            (
                portfolio_state.symbol, 
                portfolio_state.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        db.conn.commit()

        print("Mysql DB Insert Portfolio State Test Passed!")

def test_db_insert_trade_signal():

    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        # create trade signal object
        trade_signal = TradeSignal(
            timestamp=timestamp_now(),
            symbol='AAPL',
            price=100,
            quantity=10,
        )

        # insert trade signal
        db.insert_trade_signal(trade_signal)

        # check if inserted
        db.cursor.execute(
            f"""SELECT * FROM trade_signals
                WHERE symbol=%s 
                AND timestamp=%s""", 
            (
                trade_signal.symbol, 
                trade_signal.timestamp
            )
        )
        result = db.cursor.fetchone()

        assert result is not None
        assert result[1] == 'AAPL'
        assert result[2] == 10
        assert result[3] == 100

        # delete inserted row
        db.cursor.execute(
            f"""DELETE FROM trade_signals
                WHERE symbol=%s 
                AND timestamp=%s""",
            (
                trade_signal.symbol, 
                trade_signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        db.conn.commit()

        print("Mysql DB Insert Trade Signal Test Passed!")

def main():
    # run tests
    test_db_connection()
    test_db_insert_equities_historical()
    test_db_insert_portfolio_state()
    test_db_insert_trade_signal()

    print("Mysql DB Unit Tests Passed!")

if __name__ == "__main__":
    main()