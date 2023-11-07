import datetime

class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """

    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        """
        MarketEvent Constructor
        """
        self.type = "MARKET"
        self.data = {}

    def add_ticker(self, ticker, timestamp, open, low, high, close, volume):

        self.data[ticker] = {
            "timestamp": timestamp,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
        

class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, symbol, price, quantity, timestamp=datetime.datetime.now()):
        """
        SignalEvent Constructor
        symbol - ticker to trade
        price - price to trade at
        quantity - quantity to trade (negative for sell)
        """

        self.type = "SIGNAL"
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.datetime = timestamp


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity, timestamp=datetime.datetime.now()):
        """
        OrderEvent Constructor

        Parameters:
        symbol - Ticker to trade
        order_type - 'MKT' or 'LMT' for Market or Limit
        quantity - Non-negative integer for quantity
        direction - 'BUY' or 'SELL' for long or short
        """

        self.type = "ORDER"
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.datetime = timestamp


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(
        self,
        timeindex,
        symbol,
        exchange,
        quantity,
        fill_cost,
        commission=None,
    ):
        """
        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity (negative for sell)
        fill_cost - The holdings value in dollars.
        commission - An optional commission.
        """

        self.type = "FILL"
        self.timestamp = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission
    
    def calculate_commission(self):
        # TODO: make accurate commission calculation functions
        return 0
