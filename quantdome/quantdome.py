import sys
import queue
import datetime

import matplotlib.pyplot as plt

from .portfolio import *
from .execution import *
from .data      import *

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
        self.bars = HistoricalDBDataHandler(self.events, self.tickers, start_date, end_date, self.interval)
        self.strategy = None

    def add_strategy(self, strategy):
        self.strategy = strategy

    def run(self):

        if not self.strategy:
            raise TypeError("Strategy not defined. You must call Quantdome.add_strategy() prior to run()")
        # Loop over each bar
        while True:
            if self.bars.continue_backtest == True:
                self.bars.update_bars()
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
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.portfolio.update_signal(event)

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
