from strategies.strategy import Strategy
from utils.events import MarketUpdate, TradeSignal

class SimpleStrat(Strategy):

    def calculate_signals(self, market_update: MarketUpdate):
        trade_signals = []

        signal = TradeSignal(
            timestamp=market_update.timestamp,
            symbol=market_update.symbol,
            price=market_update.close,
            quantity=1
        )

        trade_signals.append(signal)

        return trade_signals
