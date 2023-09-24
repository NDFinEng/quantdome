# Local Package Improrts
from . import data

# Third Party Imports
from kafka import KafkaProducer as kp
import pandas as pd

class kafka_producer():
    def __init__(self):
        self.producer = kp(client_id='Data Handler')

''' Not sure if it is necessary to separate the two:
class backtest_kafka_producer():
    pass'''