from quantdome.execution import ExecutionHandler

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest
from decouple import config

import datetime


class AlpacaExecutionHandler():

    def __init__(self, paper=True):
        alpacaKey = config('ALPACA_KEY')
        alpacaSecret = config('ALPACA_SECRET')
        self.dataClient = StockHistoricalDataClient(alpacaKey, alpacaSecret)

    def getHistoricalData(self):

        start = datetime.datetime(2023, 6, 1)
        end = datetime.datetime(2023, 6, 2)

        request_params = StockBarsRequest(
            symbol_or_symbols=['AAPL'],
            start=start,
            end=end,
            timeframe=TimeFrame.Minute
        )

        return self.dataClient.get_stock_bars(request_params)
    
    def getQuotesData(self):

        start = datetime.datetime(2023, 6, 1)
        end = datetime.datetime(2023, 6, 2)

        request_params = StockQuotesRequest(
            symbol_or_symbols=['AAPL'],
            start=start,
            end=end
        )

        return self.dataClient.get_stock_quotes(request_params)