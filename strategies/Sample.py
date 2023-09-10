# Local Package Imports
from quantdome.strategy import Strategy
from quantdome.event import SignalEvent

class SampleStrategy(Strategy):
    """
    This is an extremely simple strategy that goes LONG all of the 
    symbols as soon as a bar is received. It will never exit a position.

    It is primarily used as a testing mechanism for the Strategy class
    as well as a benchmark upon which to compare other strategies.
    """

    def __init__(self, bars):
        pass

    def add_subscription(self, symbols):
        pass
    
    def calculate_signals(self, event):
        pass