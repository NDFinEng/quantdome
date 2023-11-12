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

from utils.events import TradeOrder, TradeFill

####################
# Global variables #
####################
SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_TRADE_FILL = SYS_CONFIG["kafka-topics"]["trade_fill"]
CONSUME_TOPIC_TRADE_ORDER = [SYS_CONFIG["kafka-topics"]["trade_order"]]

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

####################
#     Classes      #
####################


class ExecutionHandler():

    def produce(self, order: TradeOrder):

        # take in order fills ==> send to kafka
        trade_fill = TradeFill(
            timestamp=order.timestamp,
            symbol=order.symbol,
            price=order.price,
            quantity=order.quantity,
            order_id=order.order_id,
            portfolio=''
        )

        fill_json = json.dumps(trade_fill.__dict__)
        PRODUCE.produce(
            topic=PRODUCE_TOPIC_TRADE_FILL,
            value=fill_json.encode('utf-8')
        )
        PRODUCER.flush()

    def consume(self):
        CONSUMER.subscribe(CONSUME_TOPIC_TRADE_ORDER)
        logging.info(f"Subscribed to topic(s): {', '.join(CONSUME_TOPIC_TRADE_ORDER)}")
        while True:

            m_order_event = CONSUMER.poll(1)

            if m_order_event is not None:
                if m_order_event.error():
                    logging.error(m_update_event.error())
                else:
                    try:
                        time.sleep(.15)

                        log_event_received(m_order_event)

                        try:
                            trade_order = TradeOrder(**json.loads(m_order_event.value()))

                            self.produce(trade_order)

                        except Exception:
                            log_exception(
                                f"Error when processing event.value() {m_order_event.value()}",
                                sys.exc_info(),
                            )
                    except Exception:
                        log_exception(
                            f"Error when processing event.key() {m_order_event.key()}",
                            sys.exc_info(),
                        ) 

                    CONSUMER.commit(asynchronous=False)  

if __name__ == "__main__":
    handler = ExecutionHandler()
    handler.consume()