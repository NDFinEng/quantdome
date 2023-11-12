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
TOPIC_MARKET_UPDATE = self.SYS_CONFIG["kafka-topics"]["market-update"]
TOPIC_TRADE_SIGNAL = self.SYS_CONFIG["kafka-topics"]["trade-signal"]
TOPIC_FILL_ORDER = self.SYS_CONFIG["kafka-topics"]["fill-order"]

PRODUCE_TOPIC_ORDER = self.SYS_CONFIG["kafka-topics"]["trade-order"]
CONSUME_TOPICS = [
    TOPIC_MARKET_UPDATE,
    TOPIC_TRADE_SIGNAL,
    TOPIC_FILL_ORDER
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
        "client.id": f"""{SYS_CONFIG["kafka-client-id"]["microservice_portflio"]}_{HOSTNAME}"""
    }
)

# Set signal handler
GRACEFUL_SHUTDOWN = GracefulShutdown(consumer=CONSUMER)

# Set database handler
DB = MysqlHandler("quantdome_db",sys_config_file)

class PortfolioHandler():
    def __init__(self):
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
        market_update_json = json.dumps(market_update.__dict__)
        PRODUCER.produce(
            TOPIC_MARKET_UPDATE,
            value=market_update_json.encode('utf-8')
        )

        PRODUCER.flush()

    def update_fill(self, trade_fill: TradeFill):
        """Portfolio logic to update portfolio with trade fill"""

        self.positions[trade_fill.symbol] = self.positions.get(trade_fill.symbol, 0) + trade_fill.quantity
        
        # Append to TradeFill Log
        DB.insert_trade_fill(trade_fill)

    def update_portfolio(self, MarketUpdate: MarketUpdate):
        """Portfolio logic to update portfolio with market update"""

        if MarketUpdate.symbol in self.positions:
            portfolio_state = PortfolioState(
                timestamp=MarketUpdate.timestamp,
                symbol=MarketUpdate.symbol,
                value=MarketUpdate.close,
                quantity=self.positions[MarketUpdate.symbol],
                portfolio=''
            )

            # Append to PortfolioState Log
            DB.insert_portfolio_state(portfolio_state)
            

    def consume(self):

        CONSUMER.subscribe(CONSUME_TOPICS)
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
                        topic = event.topic()

                        if topic == TOPIC_TRADE_SIGNAL:
                            try:
                                event_details_json = msg.value().decode('utf-8')
                                event_details = json.loads(event_details_json)
                                trade_signal = TradeSignal(**event_details)

                                seff.produce_order(trade_signal)
                            except Exception:
                                log_exception(
                                    f'Error when processing event.value(): {event.value()}',
                                    sys.exc_info()
                                )
                        elif topic == TOPIC_FILL_ORDER:
                            try:
                                event_details_json = msg.value().decode('utf-8')
                                event_details = json.loads(event_details_json)
                                trade_fill = TradeFill(**event_details)

                                self.portfolio.update_fill(trade_fill)
                            except Exception:
                                log_exception(
                                    f'Error when processing event.value(): {event.value()}',
                                    sys.exc_info()
                                )
                        elif topic == TOPIC_MARKET_UPDATE:
                            try:
                                event_details_json = msg.value().decode('utf-8')
                                event_details = json.loads(event_details_json)
                                market_update = MarketUpdate(**event_details)

                                self.portfolio.update_portfolio(market_update)
                            except Exception:
                                log_exception(
                                    f'Error when processing event.value(): {event.value()}',
                                    sys.exc_info()
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