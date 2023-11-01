# standard library imports
import datetime
import queue
from abc import ABCMeta, abstractmethod
from math import floor

# third party imports
import numpy as np
import pandas as pd

# local package imports
from .event import FillEvent, OrderEvent
from .performance import create_sharpe_ratio, create_drawdowns

# portfolio.py

class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        raise NotImplementedError("Should implement update_signal()")

    @abstractmethod
    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        raise NotImplementedError("Should implement update_fill()")

# TODO: Needs to be more complex
class NaivePortfolio(Portfolio):
    """
    The NaivePortfolio object is designed to send orders to
    a brokerage object with a constant quantity size blindly,
    i.e. without any risk management or position sizing. It is
    used to test simpler strategies such as BuyAndHoldStrategy.
    """

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initialises the portfolio with bars and an event queue. 
        Also includes a starting datetime index and initial capital 
        (USD unless otherwise stated).

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.capital = initial_capital
        
        self.all_positions = self.construct_all_positions()
        self.all_holdings = self.construct_all_holdings()

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        return d


    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        return d
    

    def process_market_update(self, bars):

        # Update holdings
        for sym in self.symbol_list:
            self.all_holdings[sym] = bars[sym]["close"] * self.all_positions[sym]

    def update_positions_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        
        self.all_positions[fill.symbol] += fill.quantity

#TODO: Update fill price simulation
    def update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        if fill.quantity > 0:
            self.capital -= (fill.fill_cost + fill.commision)

        elif fill.quantity < 0:
            self.capital += (fill.fill_cost + fill.commision)

    def update_fill(self, event):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Generate new order from signal
        Any risk, management logic should go here

        Parameters:
        signal - The SignalEvent signal information.
        """

        return OrderEvent(signal.symbol, signal.price, signal.quantity)
        
    
    def process_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    ## data logging functions

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio such
        as Sharpe Ratio and drawdown information.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]
        return stats

# TODO: Later Versions will consider position sizing and risk management

# including the parents classes
class PortfolioState(NaivePortfolio, Portfolio):
    """
    The PortfolioState object is designed to take in 
    a portfolio and then identify and return
    the state of the portfolio.
    """

    def __init__(self, port):
        # the portfolio to be analyzed
        self.port = port

    
    def get_current_state(self):
        """
        This method gets the current state of the porfolio by returning the 
        current holdings of the portfolio

        Return:
        a tuple containing the state of the portfolio
        """

        # getting the holdings and positions
        holdings    = self.port.current_holdings
        positions   = self.port.current_positions.copy()

        state = tuple(
            holdings['datetime'],
            holdings['cash'],
            holdings['comission'],
            holdings['total'],
            positions
        )

        return state