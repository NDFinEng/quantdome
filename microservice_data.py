"""
Usage: python3 data_microservice <path/to/csv>
"""
import sys
import time
import hashlib
import logging
import os
import csv

from datetime import datetime

from utils import (
    GracefulShutdown,
    log_ini,
    save_pid,
    get_hostname,
    log_exception,
    timestamp_now,
    delivery_report,
    get_script_name,
    get_system_config,
    validate_cli_args,
    log_event_received,
    set_producer_consumer,
)

from data_handler import DatabaseDataHandler
from utils.events import MarketUpdate

####################
# Global variables #
####################
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)
save_pid(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_MARKET_UPDATE = SYS_CONFIG["kafka-topics"]["market_update"]
CONSUME_TOPIC_TRADE_SIGNAL = SYS_CONFIG["kafka-topics"]["trade_signal"]
CONSUME_TOPICS = [
    CONSUME_TOPIC_TRADE_SIGNAL,
]

_, PRODUCER, CONSUMER, _ = set_producer_consumer(
        kafka_config_file,
        producer_extra_config={
            "on_delivery": delivery_report,
            "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_update"]}_{HOSTNAME}""",
        },
        consumer_extra_config={
            "group.id": f"""{SYS_CONFIG["kafka-consumer-group-id"]["microservice_update"]}_{HOSTNAME}""",
            "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_update"]}_{HOSTNAME}""",
        },
)

GracefulShutdown = GracefulShutdown(consumer=None)

def main():    
    # Call the actual DataHandler
    handler = DatabaseDataHandler(
        config=SYS_CONFIG,
        producer=PRODUCER,
        consumer=CONSUMER,
        topic=PRODUCE_TOPIC_MARKET_UPDATE,
        tickers=["SPY"],
    )
    handler.produce()
    
if __name__ == "__main__":
    main()