from quantdome.strategy import Strategy
from quantdome.event import SignalEvent

class SimpleAppleStrategy(Strategy):

  def __init__(self, buyPrice, sellPrice):
    self.buyPrice = buyPrice
    self.sellPrice = sellPrice

  def process_signals(self, data):

    signals = []

    for d in data: # iterate through data list
      if d == 'AAPL': #only run logic on apple stocks
        if d.price < self.buyPrice: # current market price is below our buy point, let's buy
          signal = SignalEvent('AAPL', d.close, 1)

        elif d.price > self.sellPrice: #current market price is above our sell point, let's sell
          signal = SignalEvent('AAPL', d.price, -1)

        else: # otherwise the price is between, do nothing
          pass

      signals.append(signal) #append generated signal to signals list

    return signals