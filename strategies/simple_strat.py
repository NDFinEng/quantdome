from .strategy import Strategy

class SimpleStrat(Strategy):

    def calculate_signals(self, update):
        signals = []

        open_price = float(update['Open'])

        return str(open_price)
