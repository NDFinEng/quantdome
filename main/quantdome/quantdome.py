import sys
import queue
import datetime

import matplotlib.pyplot as plt

from .portfolio import *
from .execution import *
#from .data      import *

def Quantdome():

    def __init__(self, start_date, end_date, tickers):
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        self.interval = 1

        # Initialize events, datahandler, strategy, portfolio, and broker
        self.events = queue.Queue()
        self.portfolio = NaivePortfolio(self.bars, self.events, start_date)
        self.broker = SimulatedExecutionHandler(self.events)
        self.strategy = None
        self.data = None

    def set_data_csv(self, csv_dir):
        self.data = HistoricCSVDataHandler(self.events, csv_dir, self.tickers)

    def add_strategy(self, strategy):
        self.strategy = strategy

    def set_portfolio(self, portfolio):
        self.portfolio = portfolio

    def run(self):

        if not self.strategy:
            raise TypeError("Strategy not defined. You must call Quantdome.add_strategy() prior to run()")
        if not self.data:
            raise TypeError("Data source not defined.")
        
        # Loop over each bar
        while True:
            if self.data.continue_backtest == True:
                self.data.update_bars()
            else:
                break

            # Interpret events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event.data)
                            self.portfolio.update_timeindex(event.data)

                        elif event.type == 'SIGNAL':
                            self.portfolio.process_signal(event)

                        elif event.type == 'ORDER':
                            self.broker.execute_order(event)

                        elif event.type == 'FILL':
                            self.portfolio.update_fill(event)


    def get_results(self):
        # Retrieve backtest results 
        self.portfolio.create_equity_curve_dataframe()
        stats = self.portfolio.output_summary_stats()

        # Print statistics
        for stat in stats:
            print(f'{stat[0]}: {stat[1]}')

        # Display equity curve
        fig, ax = plt.subplots()
        ax.plot(self.portfolio.equity_curve.index.values, self.portfolio.equity_curve.loc[:,"total"])
        ax.set(xlabel='Date', ylabel='Total Return', title='Equity Curve')
        ax.grid()
        fig.savefig('eq.png')
        plt.show()
