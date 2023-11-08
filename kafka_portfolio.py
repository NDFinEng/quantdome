## Microservice to translate signals to orders, track portfolio

import sys
import json
import logging
import time
import hashlib

from utils import *
from .main.quantdome.portfolio import *
from .main.quantdome.event import *

class PortfolioHandler():
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        
        # Global Variables
        SCRIPT = get_script_name(__file__)
        HOSTNAME = get_hostname()

        log_ini(SCRIPT)
        save_pid(SCRIPT)

        # Validate command arguments
        kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

        # Get system config file
        self.SYS_CONFIG = get_system_config(sys_config_file)

        # Set producer / consumer objects
        self.PRODUCE_TOPIC_ORDER = self.SYS_CONFIG["kafka-topics"]["trade-order"]
        self.CONSUME_TOPICS = [
            self.SYS_CONFIG["kafka-topics"]["trade-signal"],
            #self.SYS_CONFIG["kafka-topics"]["fill-order"]
        ]

        # TODO: Create second consumer to listen to fill orders 
        # Other option is to handle different signal types in a single consumer (in receive_signal())
        _, self.PRODUCER, self.CONSUMER, _ = set_producer_consumer(
            kafka_config_file,
            producer_extra_config={
                "on_delivery": delivery_report,
                "client.id": f"""{self.SYS_CONFIG["kafka-client-id"]["microservice_order"]}_{HOSTNAME}"""
            },
            consumer_extra_config={
                "group.id": f"""{self.SYS_CONFIG["kafka-consumer-group-id"]["microservice_signal"]}_{HOSTNAME}""",
                "client.id": f"""{self.SYS_CONFIG["kafka-client-id"]["microservice_signal"]}_{HOSTNAME}"""
            }
        )

        # Set signal handler
        self.GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=self.CONSUMER)

    def send_order(
        self,
        symbol: str,
        order_type: str,
        quantity: int,
        direction: str
    ):
        # Produce Order Event with arguments
        self.PRODUCER.produce(
            self.PRODUCE_TOPIC_ORDER,
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
        self.PRODUCER.flush()

    def receive_signal(self):
        self.CONSUMER.subscribe(self.CONSUME_TOPICS)
        logging.info(f"Subscribed to topic(s): {','.join(self.CONSUME_TOPICS)}")
        while True:
            with self.GRACEFUL_SHUTDOWN as _:

                # Pull event
                event = self.CONSUMER.poll(1)

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
                            price = signal_details["price"]
                            quantity = signal_details["quantity"]
                            timestamp = signal_details["datetime"]
                        except Exception:
                            log_exception(
                                f'Error when processing event.value(): {event.value()}',
                                sys.exc_info()
                            )
                        else:
                            # Generate seed
                            seed = int(
                                hashlib.md5(
                                    f"""{symbol@price@quantity@timestamp}""".encode()
                                ).hexdigest()[-4:0],
                                16
                            )

                            # TODO: This will need to be changed with updated portfolio.py
                            order = self.portfolio.generate_naive_order(SignalEvent(symbol, price, quantity, timestamp))

                            # Call producer
                            self.send_order(
                                order.symbol,
                                order.order_type,
                                order.quantity,
                                order.timestamp
                            )

                    # Manual commit
                    self.CONSUMER.commit(asynchronous=False)
            

# Main
if __name__ == "__main__":
    # start consumer
    # TODO: Current portfolio implementation requires direct access to data handler,
    # this needs to be changed for kafka implementation
    ph = PortfolioHandler(NaivePortfolio())
    ph.receive_signal()