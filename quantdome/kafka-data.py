# Local Package Improrts
from . import data

# Third Party Imports
from kafka import KafkaProducer as kp
import pandas as pd

class kafka_producer():
    def __init__(self):
        server_id = 'localhost:9092'
        self.producer = kp(bootstrap_servers=server_id, client_id='Data Handler')

        if not self.producer.bootstrap_connected():
            raise Exception(f'Cannot connect to {server_id}. Please check connection and try again.')


''' Not sure if it is necessary to separate the two:
class backtest_kafka_producer():
    pass'''