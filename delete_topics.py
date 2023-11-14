# Delete topics and ksqlDB Streams

import sys
import time
import logging

from confluent_kafka.admin import NewTopic

from utils import (
    ksqldb,
    log_ini,
    log_exception,
    get_script_name,
    validate_cli_args,
    get_system_config,
    get_topic_partitions,
    set_producer_consumer,
)

####################
# Global variables #
####################
SCRIPT = get_script_name(__file__)
log_ini(SCRIPT, to_disk=False)

# Validate command arguments
kafka_config_file, sys_config_file = validate_cli_args(SCRIPT)

# Get system config file
SYS_CONFIG = get_system_config(sys_config_file)

# Set producer/consumer objects
KAFKA_CONFIG, _, _, ADMIN_CLIENT = set_producer_consumer(
    kafka_config_file,
    disable_producer=True,
    disable_consumer=True,
)

TOPIC_MARKET_UPDATE = SYS_CONFIG["kafka-topics"]["market_update"]
STREAM_MARKET_UPDATE = TOPIC_MARKET_UPDATE.replace("-", "_").upper()

TOPIC_TRADE_SIGNAL = SYS_CONFIG["kafka-topics"]["trade_signal"]
STREAM_TRADE_SIGNAL = TOPIC_TRADE_SIGNAL.replace("-", "_").upper()

TOPIC_TRADE_ORDER = SYS_CONFIG["kafka-topics"]["trade_order"]
STREAM_TRADE_ORDER = TOPIC_TRADE_ORDER.replace("-", "_").upper()

TOPIC_TRADE_FILL = SYS_CONFIG["kafka-topics"]["trade_fill"]
STREAM_TRADE_FILL = TOPIC_TRADE_FILL.replace("-", "_").upper()

TOPIC_STATUS = SYS_CONFIG["kafka-topics"]["trade_status"]
STREAM_STATUS = TOPIC_STATUS.replace("-", "_").upper()


# Persistent queries to push all statuses generated by each stream to the status stream
PERSISTENT_QUERIES = {
    f"PERSISTENT_QUERY_{stream}": f"""INSERT INTO {STREAM_STATUS} SELECT order_id, status, timestamp FROM {stream} EMIT CHANGES;"""
    for stream in [
        STREAM_MARKET_UPDATE,
        STREAM_TRADE_SIGNAL,
        STREAM_TRADE_ORDER,
        STREAM_TRADE_FILL,
    ]
}

KSQL_STATEMENTS = {
    STREAM_MARKET_UPDATE: f"""CREATE STREAM IF NOT EXISTS {STREAM_MARKET_UPDATE} (
        
    )
    """
}

if __name__ == "__main__":
    # Create topics
    num_partitions = int(SYS_CONFIG["kafka-topic-config"]["num_partitions"])
    replication_factor = int(SYS_CONFIG["kafka-topic-config"]["replication_factor"])
    for alias, topic in SYS_CONFIG["kafka-topics"].items():
        logging.info(
            f"Deleting topic {alias} as '{topic}' with {num_partitions} partition(s) and replication factor {replication_factor}..."
        )
        try:
            partitions = get_topic_partitions(
                ADMIN_CLIENT,
                topic,
                default_partition_number=0,
            )
            # If topic exists, delete it
            if partitions != 0:
                logging.info(f"Topic {topic} already exists. Deleting...")
                ADMIN_CLIENT.delete_topics([topic])
                time.sleep(1)
                logging.info(f"Topic {topic} deleted.")

        except Exception as e:
            log_exception(e, SCRIPT)
            sys.exit(1)