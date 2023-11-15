# test strategy handler
import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from microservice_strategy import StrategyHandler
from utils import *

####################

SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)
save_pid(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_TRADE_SIGNAL = SYS_CONFIG["kafka-topics"]["trade_signal"]
CONSUME_TOPIC_MARKET_UPDATE = [SYS_CONFIG["kafka-topics"]["market_update"]]

_, PRODUCER, CONSUMER, _ = set_producer_consumer(
    kafka_config_file,
    producer_extra_config={
        #SECOND ARGUMENT OF CLIENT ID IS TEMPORARY
        "on_delivery": delivery_report,
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_signal"]}_{HOSTNAME}""",
    },
    consumer_extra_config={
        "group.id": f"""{SYS_CONFIG["kafka-consumer-group-id"]["microservice_update"]}_{HOSTNAME}""",
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_update"]}_{HOSTNAME}""",
    },  
)
        
GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=CONSUMER)


def test_strategy_handler():

    pass

def main():
    test_strategy_handler()

    print("Strategy Handler Tests Passed!")

if __name__ == "__main__":
    main()