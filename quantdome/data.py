# Standard Library Imports
import datetime
import time # for the sleep since Alpacas is up to the minute
import os, os.path
from abc import ABCMeta, abstractmethod

# Third Party Imports
import pandas as pd
from alpaca.data.live import StockDataStream

# Local Package Imports
from .event import MarketEvent


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OLHCVI) for each symbol requested.

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bar to the latest symbol structure
        for all symbols in the symbol list.
        """
        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.

        For this handler it will be assumed that the data is
        taken from Yahoo. Thus its format will be respected.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=[
                    'datetime', 'open', 'high', 
                    'low', 'close', 'adj_close', 'volume'
                ]
            )
            self.symbol_data[s].sort_index(inplace=True)

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index, method='pad'
            )
            self.symbol_data[s]["returns"] = self.symbol_data[s]["adj_close"].pct_change().dropna()

            ''' The following line of code was in the original tutorial, but the next
                for loop throws an error because it turns each Dataframe into a generator.
            self.symbol_data[s] = self.symbol_data[s].iterrows()'''

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of 
        (sybmbol, datetime, open, low, high, close, volume).
        """
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.datetime.strptime(str(b[0]), '%Y-%m-%d %H:%M:%S'), 
                        b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])
            
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
        else:
            return bars_list[-N:]
        
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())


class LiveDataHandler(DataHandler):
    """
    LiveDataHandler is designed to obtain live 
    data from the Alpaca API
    """
    def __init__(self, events, symbol_list):
        '''
        Initializing the data handler with some Alpaca keys etc

        Parameters:
        events - The Event Queue
        symbol_list - A list of symbol strings
        '''

        self.events         = events
        self.symbol_list    = symbol_list
        # api_key             = decouple.config('ALPACA_KEY')
        # api_secret          = decouple.config('ALPACA_SECRET')

        stock_stream = StockDataStream('PK3CUW84A4FCFA3WJGWZ', 'hkhoufIN259azCiafqgyQlfcgdvYShhmgH552brm')

        # Structure to store the data that we've been collecting
        self.latest_symbol_data = {} 

        for s in symbol_list:
            stock_stream.subscribe_bars(self._get_new_bar, s)
            self.latest_symbol_data[s] = []
   
        self.run_connection(stock_stream)

    async def _get_new_bar(self, bars):
        """
        Returns the latest bar from Alpaca as a tuple of 
        (symbol, date, open, low, high, close, volume)
        """
        present_time = datetime.datetime.fromtimestamp(bars.timestamp.timestamp(), tz=datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
        data = tuple([bars.symbol, present_time, bars.open, bars.low, bars.high, bars.close, bars.volume])

        print(data)
        self.latest_symbol_data[bars.symbol].append(data)
        self.events.put(MarketEvent())

    def run_connection(self, stream):
        '''Initiates a running connection. When connection is terminated 
        (i.e. via ctrl+c) then the program exits. Severing the connection 
        takes a few seconds.'''
        stream.run()

        print("Connection closed.")
        exit(0)
        
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol was not entered in the symbol list.")
        else:
            return bars_list[-N:]
        
    def update_bars(self):
        """
        Pushes the latest bar to the latest symbol structure
        for all symbols in the symbol list.
        """
        raise NotImplementedError("Live data handlers do not require manual calls to update bars, as bars are updated automatically.")