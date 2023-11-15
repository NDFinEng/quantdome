# simple strategy unit tests

import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from strategies.simple_strat import SimpleStrat
from utils.events import MarketUpdate

def test_simple_strat():

    # create simple strat object
    simple_strat = SimpleStrat()

    # create market update object
    market_update = MarketUpdate(
        timestamp=123456789,
        symbol="GOOG",
        open=1000.00,
        high=1000.00,
        low=1000.00,
        close=800.00,
        volume=1000
    )

    # calculate signals
    signals = simple_strat.calculate_signals(market_update)

    # check signals
    assert len(signals) == 1
    assert signals[0].timestamp == 123456789
    assert signals[0].symbol == "GOOG"
    assert signals[0].price == 800.00
    assert signals[0].quantity == 1
    
    print("Simple Strategy Unit Test Passed!")

def main():
    # run tests
    test_simple_strat()

if __name__ == "__main__":
    main()