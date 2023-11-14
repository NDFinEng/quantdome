import sys
import json
import time
import logging

from utils import *
from utils.events import *
from utils.db.mysql import MysqlHandler

from strategies.simple_strat import SimpleStrat

####################
# Global variables #
####################

SCRIPT = get_script_name(__file__)
HOSTNAME = get_hostname()

log_ini(SCRIPT)
save_pid(SCRIPT)

kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

SYS_CONFIG = get_system_config(sys_config_file)

PRODUCE_TOPIC_TRADE_SIGNAL = SYS_CONFIG["kafka-topics"]["trade_signal"]
CONSUME_TOPIC_MARKET_UPDATE = SYS_CONFIG["kafka-topics"]["market_update"]
CONSUME_TOPICS = [
    CONSUME_TOPIC_MARKET_UPDATE
]

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

    def __init__(self, config, producer, consumer, topic, strategy):
        # Configurations
        self.config = config
        self.producer = producer
        self.consumer = consumer
        self.topic = topic

        # Strategy that is being implemented
        self.strategy = strategy

    def produce(self, signals: list[TradeSignal]):

        for signal in signals:

            with MysqlHandler('quantdome_db', SYS_CONFIG) as db:
                db.insert_trade_signal(signal)

            signal_json = json.dumps(signal.__dict__).encode('utf-8')
            self.producer.produce(
                topic=PRODUCE_TOPIC_TRADE_SIGNAL,
                value=signal_json
            )
            self.producer.flush()


    def consume(self):
        # Consuming Market Updates
        self.consumer.subscribe(self.topic)
        logging.info(f"Subscribed to topic(s): {', '.join(self.topic)}")
        while True:
            # Consuming some Market Update
            m_update_event = self.consumer.poll(1)

            if m_update_event is not None:
                if m_update_event.error():
                    logging.error(m_update_event.error())
                else:
                    try:
                        # Add a little delay just to allow the logs on the previous micro-service to be displayed first

                        log_event_received(m_update_event)

                        #update = m_update_event.key().decode()
                            
                        try:
                            # Market Update
                            update = MarketUpdate(**json.loads(m_update_event.value().decode('utf-8')))

                            # Generate Signal Based on Strategy
                            signals = self.strategy.calculate_signals(update)
                            
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

                    self.consumer.commit(asynchronous=False)  

def main():
    strat = SimpleStrat()
    handler = StrategyHandler(
        config=SYS_CONFIG,
        producer=PRODUCER,
        consumer=CONSUMER,
        topic=CONSUME_TOPICS,
        strategy=strat
    )
    handler.consume()

if __name__ == "__main__":
    main()
