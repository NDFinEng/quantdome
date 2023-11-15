## Microservice to translate signals to orders, track portfolio

import sys
import json
import logging
import time
import hashlib

from utils import *
from utils.events import *
from utils.db.mysql import MysqlHandler

# Global Variables
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)
save_pid(SCRIPT)

# Validate command arguments
kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

# Get system config file
SYS_CONFIG = get_system_config(sys_config_file)

# Set producer / consumer objects
TOPIC_MARKET_UPDATE = SYS_CONFIG["kafka-topics"]["market_update"]
TOPIC_TRADE_SIGNAL = SYS_CONFIG["kafka-topics"]["trade_signal"]
TOPIC_TRADE_FILL = SYS_CONFIG["kafka-topics"]["trade_fill"]

PRODUCE_TOPIC_ORDER = SYS_CONFIG["kafka-topics"]["trade_order"]
CONSUME_TOPICS = [
    TOPIC_TRADE_SIGNAL,
    TOPIC_TRADE_FILL
]

# TODO: Create second consumer to listen to fill orders 
# Other option is to handle different signal types in a single consumer (in receive_signal())
_, PRODUCER, CONSUMER, _ = set_producer_consumer(
    kafka_config_file,
    producer_extra_config={
        "on_delivery": delivery_report,
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_portfolio"]}_{HOSTNAME}"""
    },
    consumer_extra_config={
        "group.id": f"""{SYS_CONFIG["kafka-consumer-group-id"]["microservice_portfolio"]}_{HOSTNAME}""",
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_portfolio"]}_{HOSTNAME}"""
    }
)

# Set signal handler
GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=CONSUMER)

# Set database handler

class PortfolioHandler():
    def __init__(self, config, producer, consumer, topic):
        # Configurations
        self.config = config
        self.producer = producer
        self.consumer = consumer
        self.topic = topic

        self.positions = {}

    def produce_order(self, trade_signal: TradeSignal):
        """Portfolio logic to produce trade order from trade signal"""

        trade_order = TradeOrder(
            timestamp=trade_signal.timestamp,
            symbol=trade_signal.symbol,
            price=trade_signal.price,
            quantity=trade_signal.quantity
        )

        # Send order to kafka
        trade_order_json = json.dumps(trade_order.__dict__)
        self.producer.produce(
            topic=PRODUCE_TOPIC_ORDER,
            value=trade_order_json.encode('utf-8')
        )

        self.producer.flush()

    def update_fill(self, trade_fill: TradeFill):
        """Portfolio logic to update portfolio with trade fill"""

        self.positions[trade_fill.symbol] = self.positions.get(trade_fill.symbol, 0) + trade_fill.quantity
        
        # Append to TradeFill Log
        self.update_portfolio(trade_fill)

    def update_portfolio(self, trade_fill: TradeFill):
        """Portfolio logic to update portfolio with market update"""

        if trade_fill.symbol in self.positions:
            portfolio_state = PortfolioState(
                timestamp=trade_fill.timestamp,
                symbol=trade_fill.symbol,
                quantity=self.positions[trade_fill.symbol],
                portfolio=''
            )

            # Append to PortfolioState Log
            with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
                db.insert_portfolio_state(portfolio_state)

    def consume(self):

        self.consumer.subscribe(CONSUME_TOPICS)
        logging.info(f"Subscribed to topic(s): {' '.join(CONSUME_TOPICS)}")
        while True:
            # Pull event
            event = self.consumer.poll(1)

            # Check for errors
            if event is not None:
                if event.error():
                    logging.error(event.error())
                else:
                    log_event_received(event)
                    topic = event.topic()

                    if topic == TOPIC_TRADE_SIGNAL:
                        try:
                            event_details_json = event.value().decode('utf-8')
                            event_details = json.loads(event_details_json)
                            trade_signal = TradeSignal(**event_details)

                            self.produce_order(trade_signal)

                        except Exception:
                            log_exception(
                                f'Error when processing event.value(): {event.value()}',
                                sys.exc_info()
                            )
                    elif topic == TOPIC_TRADE_FILL:
                        try:
                            event_details_json = event.value().decode('utf-8')
                            event_details = json.loads(event_details_json)
                            trade_fill = TradeFill(**event_details)

                            self.update_fill(trade_fill)
                        except Exception:
                            log_exception(
                                f'Error when processing event.value(): {event.value()}',
                                sys.exc_info()
                            )


                # Manual commit
                self.consumer.commit(asynchronous=False)

def main():
    # Call the actual portfolio handler
    handler = PortfolioHandler(
        config=SYS_CONFIG,
        producer=PRODUCER,
        consumer=CONSUMER,
        topic=PRODUCE_TOPIC_ORDER
    )
    handler.consume()
            

# Main
if __name__ == "__main__":
    main()