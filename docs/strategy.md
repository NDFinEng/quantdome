# Strategy Module Overview
The core of every algorithm is defined by and inherits from the `quantdome.strategy` class.  In it's most basic form the strategy class will recieve market updates and process and send signals if desired.  These signals are then processed by the `portfolio` and sent to the brokers as orders if approved. (View `quantdome.portfolio` to learn about approval settings.)

## Structure Overview
Each strategy must invoke the following methods:
1. `__init__(self)`
2. `set_tickers(self, tickers: list[string]) -> None`
3. `process_signals(self, data: quantdome.MarketData) -> list[quantdome.SignalEvent]`

Let's now look at what each method does:
### `__init__(self)`
- *Inputs*: can add any inputs as necessary
- *Outputs*: none

This is the initialization or constructor method for the `strategy` class.  It defines any member variables needed for the class and can take any inputs as desired.

### `set_tickers(self, tickers: list[string]) -> None`
- *Inputs*: a list of tickers (`strings`) which the strategy should listen for
- *Outputs*: none

This method sets the tickers which the strategy should listen for.  This allows input to the following method to be reduced to only necessary data rather than all market noise.
This should be set before the strategy is turned on.

### `process_signals(self, data: quantdome.MarketData) -> list[quantdome.SignalEvent]`
- *Inputs*: the quantdome market data structure containing the latest market data
- *Outputs*: a list of all signals produced by the strategy

This is the meat of every strategy.  Everytime a market update is recieved, this method will run the designed strategy and emit any possible trade signals.  This method may call other optional functions defined by the user and may update any state variables.  If no trade signals are wished to be sent given the current market state, an empty list `[]` should be returned.


## Quick Example

Here's a quick example of a very simple strategy that will buy Apple stock if it breaks below $180.00 and sell Apple stock if it rallies above $190.00

```Python
class SimpleAppleStrategy(Strategy):

  def __init__(self, buyPrice, sellPrice):
    self.buyPrice = buyPrice
    self.sellPrice = sellPrice

  def process_signals(self, data):

    signals = []

    for d in data: # iterate through data list
      if d == 'AAPL': #only run logic on apple stocks
        if d.price < buyPrice: # current market price is below our buy point, let's buy
          signal = MarketSignal(d.price, 1)

        elif d.price > sellPrice: #current market price is above our sell point, let's sell
          signal = MarketSignal(d.price, -1)

        else: # otherwise the price is between, do nothing
          pass

      signals.append(signal) #append generated signal to signals list

    return signals
```
**Note:** The strategy does not have to redefine `set_tickers()` as it is properly defined in the `Strategy` base class
