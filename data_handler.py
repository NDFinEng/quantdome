# Data Handler base class
from abc import ABCMeta, abstractmethod
from utils.events import MarketUpdate
from utils.db.mysql import MysqlHandler
import json


class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self, config, producer, topic):
        self.config = config
        self.producer = producer
        self.topic = topic

    @abstractmethod
    def produce(self):
        """
        Provides the mechanisms to produce data.
        """
        raise NotImplementedError("Should implement produce()")


# Database Data Handler
class DatabaseDataHandler(DataHandler):
    def __init__(self, config, producer, topic, tickers):
        super().__init__(config, producer, topic)
        self.tickers = tickers
    
    def produce(self):

        with MysqlHandler('quantdome_db', self.config) as db:
            for ticker in self.tickers:
                # Get historical data from database
                historical_data = db.get_equities_historical(ticker)

                # Produce to Kafka
                for row in historical_data:
                    market_update = MarketUpdate(
                        timestamp=int(row[0].timestamp()),
                        symbol=row[1],
                        high=float(row[2]),
                        low=float(row[3]),
                        open=float(row[4]),
                        close=float(row[5]),
                        volume=int(row[6]),
                    )

                    market_update_json = json.dumps(market_update.__dict__)

                    self.producer.produce(
                        self.topic,
                        value=market_update_json.encode('utf-8')
                    )

                    self.producer.flush()



# CSV Data Handler
class CSVDataHandler(DataHandler):
    def __init__(self, csv_file, tickers): # Can edit later to pass in producer object if global variables gets messy
        self.csv_file = csv_file
        #self.ticker = ticker
    
    def read_csv(self, csv_file: str): # returns reader object
        with open(csv_file) as f:
            return csv.reader(csv_file)
    
    def produce(self):
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            # skip header row
            next(reader,None)
            for line in reader:
                try:
                    Date, Open, High, Low, Close, AdjClose, Volume = line
                except Exception as e:
                    print("Exception encountered", e)
                    return

                # Produce to Kafka
                market_update = MarketUpdate(
                    timestamp=int(datetime.strptime(Date, "%m/%d/%Y").timestamp()),
                    symbol="GOOG",
                    high=float(High),
                    low=float(Low),
                    open=float(Open),
                    close=float(Close),
                    volume=int(Volume),
                )

                market_update_json = json.dumps(market_update.__dict__)

                PRODUCER.produce(
                    PRODUCE_TOPIC_MARKET_UPDATE,
                    value=market_update_json.encode('utf-8')
                )
                PRODUCER.flush()
        #return self.read_csv(self.csv_file) # TODO Change Later, just for basic unit tests now
