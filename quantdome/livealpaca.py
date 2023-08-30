from quantdome.execution import ExecutionHandler

from alpaca.data.live import StockDataStream
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest
from decouple import config

from datetime import datetime

import nest_asyncio
nest_asyncio.apply()

class LiveAlpacaExecutionHandler():

    def __init__(self, paper=True):
        alpacaKey = config('ALPACA_KEY')
        alpacaSecret = config('ALPACA_SECRET')
        # This should be getting the live data
        self.dataClient = StockDataStream(alpacaKey, alpacaSecret)


    # this is based off of Peter's existing code, unsure if the same things
    # are applicable to the StockDataStream

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
    

    # this is a variation of what we had attempted during v_2 
    # this might be more in the right direction?
    # 

    # async handler
    async def bars_data_handler(self, data):
        # real-time data will be displayed here
        # as it arrives
        print(data)
        print("===")

        # TODO if this is properly connecting and getting the data, we need
        # to store it in a manner that is compatable with the other data we have


        try:
            self.dataClient.subscribe_bars(bars_data_handler, "AAPL")
            self.dataClient.run()

        except Exception as e:
            print(e)    
