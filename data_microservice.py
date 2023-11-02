"""
Usage: python3 data_microservice <path/to/csv>
"""


import sys
import json
import time
import hashlib
import logging
import os
import csv

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

####################
# Global variables #
####################
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_MARKET_UPDATE = SYS_CONFIG["kafka-topics"]["market_update"]

_, PRODUCER, _, _ = set_producer_consumer(
        kafka_config_file,
        producer_extra_config={
            "on_delivery": delivery_report,
            "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_update"]}_{HOSTNAME}""",
        },
        disable_consumer = True
)

def main():
    # Basic checking for valid input
    if len(sys.argv[1:]) < 3:
        print("Incorrect Usage in data_microservice. Usage; python3 data_microservice <path/to/csv>")
        exit(1)
    if not os.path.isfile(sys.argv[-1]):
        print("Not a valid file")
        exit(1)
    

    # Call the actual DataHandler
    Handler = DataHandler(sys.argv[-1],[])
    return(Handler.produce())

    #GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=CONSUMER) #Might need this later

class DataHandler:
    def __init__(self, csv_file, tickers): # Can edit later to pass in producer object if global variables gets messy
        self.csv_file = csv_file
        #self.ticker = ticker
    
    def read_csv(self, csv_file: str): # returns reader object
        with open(csv_file) as f:
            return csv.reader(csv_file)
    
    def produce(self):
        return(self._produce())


    def _produce(self):
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            # skip header row
            next(reader,None)
            for line in reader:
                try:
                    Date, Open, High, Low, Close, AdjClose, Volume = line
                except Exception as e:
                    print("Exception encountered", e)
                    return
                PRODUCER.produce(
                    PRODUCE_TOPIC_MARKET_UPDATE,
                    value=json.dumps(
                        {
                            "Date": Date,
                            "Open": Open,
                            "High": High,
                            "Low": Low,
                            "Close": Close,
                            "Adj Close": AdjClose,
                            "Volume": Volume,
                            "Timestamp": timestamp_now(),
                        }
                    ).encode(),
                )
                PRODUCER.flush()
        #return self.read_csv(self.csv_file) # TODO Change Later, just for basic unit tests now

    


if __name__ == "__main__":
    main()