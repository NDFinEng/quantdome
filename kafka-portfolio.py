## Microservice to translate signals to orders, track portfolio

import sys
import json
import logging
import time
import hashlib

from utils import *
from .main.quantdome.portfolio import *

# Global Variables
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

# Validate command arguments
kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

# Get system config file
SYS_CONFIG = get_system_config(sys_config_file)

# Set producer / consumer objects
PRODUCE_TOPIC_ORDER = SYS_CONFIG["kafka-topics"]["trade-order"]
CONSUME_TOPICS = [
    SYS_CONFIG["kafka-topics"]["trade-signal"],
    #SYS_CONFIG["kafka-topics"]["fill-order"]
]

# TODO: Create second consumer to listen to fill orders 
# Other option is to handle different signal types in a single consumer (in receive_signal())
_, PRODUCER, CONSUMER, _ = set_producer_consumer(
    kafka_config_file,
    producer_extra_config={
        "on_delivery": delivery_report,
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_order"]}_{HOSTNAME}"""
    },
    consumer_extra_config={
        "group.id": f"""{SYS_CONFIG["kafka-consumer-group-id"]["microservice_signal"]}_{HOSTNAME}""",
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_signal"]}_{HOSTNAME}"""
    }

)

# Set signal handler
GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=CONSUMER)

def send_order(
        symbol: str,
        order_type: str,
        quantity: int,
        direction: str
):
    # Produce Order Event with arguments
    PRODUCER.produce(
        PRODUCE_TOPIC_ORDER,
        value=json.dumps(
            {
                "symbol": symbol,
                "order_type": order_type,
                "quantity": quantity,
                "direction": direction
            }
        ).encode()
    )
    # Send Order Event
    PRODUCER.flush()

def receive_signal():
    CONSUMER.subscribe(CONSUME_TOPICS)
    logging.info(f"Subscribed to topic(s): {','.join(CONSUME_TOPICS)}")
    while True:
        with GRACEFUL_SHUTDOWN as _:

            # Pull event
            event = CONSUMER.poll(1)

            # Check for errors
            if event is not None:
                if event.error():
                    logging.error(event.error())
                else:

                    # Small delay to allow logs on previous microservice to display first (can we remove?)
                    time.sleep(0.15)

                    log_event_received(event)

                    try:
                        # Unpack event
                        signal_details = json.loads(event.value.decode())
                        symbol = signal_details["symbol"]
                        timestamp = signal_details["datetime"]
                        signal_type = signal_details["signal_type"]
                    except Exception:
                        log_exception(
                            f'Error when processing event.value(): {event.value()}',
                            sys.exc_info()
                        )
                    else:
                        # Generate seed
                        seed = int(
                            hashlib.md5(
                                f"""{symbol@timestamp@signal_type}""".encode()
                            ).hexdigest()[-4:0],
                            16
                        )

                        # TODO: Use portfolio.py to generate order_type, quantity, and direction value

                        # Call producer
                        send_order(
                            symbol,
                            order_type,
                            quantity,
                            direction
                        )