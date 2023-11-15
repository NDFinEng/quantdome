# data microservice
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from data_handler import DatabaseDataHandler
from utils.db.mysql import MysqlHandler
from utils import *
from utils.events import MarketUpdate

SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_TEST = SYS_CONFIG["kafka-topics"]["test"]

_, PRODUCER, _, _ = set_producer_consumer(
    kafka_config_file,
    producer_extra_config={
        "on_delivery": delivery_report,
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["test"]}_{HOSTNAME}""",
    },
    disable_consumer = True
)

GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=None)

def test_database_data_handler():

    # add test data to database
    market_update = MarketUpdate(
        symbol='TEST',
        timestamp=timestamp_now(),
        high=100,
        low=50,
        open=75,
        close=75,
        volume=1000,
    )

    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        db.insert_equities_historical(market_update)

    # create data handler
    handler = DatabaseDataHandler(
        config=SYS_CONFIG,
        producer=PRODUCER,
        topic=PRODUCE_TOPIC_TEST,
        tickers=["TEST"],
    )

    handler.produce()

    # check if data was produced
    PRODUCER.flush()

    # remove test data from db
    with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
        db.cursor.execute(
            f"""DELETE FROM equities_historical 
                WHERE symbol=%s 
                AND timestamp=%s""", 
            (
                market_update.symbol, 
                market_update.timestamp
            )
        )

def main():
    test_database_data_handler()
    print("All tests passed!")

if __name__ == "__main__":
    main()