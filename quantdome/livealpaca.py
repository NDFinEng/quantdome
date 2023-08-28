from quantdome.execution import ExecutionHandler

from alpaca.data.live import StockDataStream
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest
from decouple import config

from datetime import datetime


class LiveAlpacaExecutionHandler():

    def __init__(self, paper=True):
        alpacaKey = config('ALPACA_KEY')
        alpacaSecret = config('ALPACA_SECRET')
        self.dataClient = StockDataStream(alpacaKey, alpacaSecret)

    def getLiveData(self, symbol='AAPL'):
        
        dt_now = datetime.now()

        start = dt_now
        end = dt_now

        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            start=start,
            end=end,
            timeframe=TimeFrame.Minute
        )

        return self.dataClient.get_stock_bars(request_params)
    
    # for test purposes I have AAPL hard coded in
    def getLiveQuotesData(self, symbol='AAPL'):
        
        dt_now = datetime.now()

        start = dt_now
        end = dt_now

        request_params = StockQuotesRequest(
            symbol_or_symbols=[symbol],
            start=start,
            end=end
        )

        return self.dataClient.get_stock_quotes(request_params)
