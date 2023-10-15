# Local Package Improrts
from . import data

# Third Party Imports
from kafka import KafkaProducer as kp
from json import dumps

class kafka_producer():
    def __init__(self):
        server_id = 'quantdome.crc.nd.edu:8092'
        self.producer = kp(
            bootstrap_servers=server_id, 
            client_id='Data Handler',
            value_serializer=lambda x: dumps(x).encode('utf-8')
        )

        if not self.producer.bootstrap_connected():
            raise Exception(f'Cannot connect to {server_id}. Please check connection and try again.')
        
    def send(self, type, name, value):
        self.producer.send(type, value=value, partition=name)

    def names(self, type):
        for name in self.producer.partitions_for(type):
            print(name)