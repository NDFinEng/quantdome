import sys
import json
import time
import logging

from utils import *

from strategies.simple_strat import SimpleStrat

####################
# Global variables #
####################

SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)

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

####################
#     Classes      #
####################


class StrategyHandler():

    def __init__(self, strategy):
        # Strategy that is being implemented
        self.strategy = strategy

    def produce(self, signals):
        # take in trade signals ==> send to kafka

        # Producing Trade Signals
        # Produce to kafka topic
        PRODUCER.produce(
            PRODUCE_TOPIC_TRADE_SIGNAL,
            # KEY?
            key=signals,
            value=json.dumps(
                {
                    "trading-signal": signals,
                    "timestamp": timestamp_now(),
                }
            ).encode(),
        )
        PRODUCER.flush()


    def consume(self):
        # Consuming Market Updates
        CONSUMER.subscribe(CONSUME_TOPIC_MARKET_UPDATE)
        logging.info(f"Subscribed to topic(s): {', '.join(CONSUME_TOPIC_MARKET_UPDATE)}")
        while True:
            # Consuming some Market Update
            m_update_event = CONSUMER.poll(1)

            if m_update_event is not None:
                if m_update_event.error():
                    logging.error(m_update_event.error())
                else:
                    try:
                        # Add a little delay just to allow the logs on the previous micro-service to be displayed first
                        time.sleep(.15)

                        log_event_received(m_update_event)

                        #update = m_update_event.key().decode()
                            
                        try:
                            # Market Update
                            update = json.loads(m_update_event.value().decode())

                            # Generate Signal Based on Strategy
                            # STRATEGY.PY ==> generates signals
                            signals = self.strategy.calculate_signals(update=update)
                            
                            # Produce the Generated Trade Signal
                            self.produce(signals)
                            
                        except Exception:
                            log_exception(
                                f"Error when processing event.value() {m_update_event.value()}",
                                sys.exc_info(),
                            )
                    except Exception:
                        log_exception(
                            f"Error when processing event.key() {m_update_event.key()}",
                            sys.exc_info(),
                        ) 

                    CONSUMER.commit(asynchronous=False)  



if __name__ == "__main__":
    strat = SimpleStrat()
    test = StrategyHandler(strat)
    test.consume()
    #test.produce()    
