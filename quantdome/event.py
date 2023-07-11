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


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, symbol, datetime, signal_type):
        """
        SignalEvent Constructor

        Parameters:
        symbol - Ticker symbol
        datetime - Timestamp at which the signal was generated
        signal_type - 'LONG' or 'SHORT'
        """

        self.type = "SIGNAL"
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, symbol, order_type, quantity, direction):
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
        self.direction = direction

    def __repr__(self):
        """
        Outputs the values within the Order.
        """
        print(
            f"Order: Symbol={self.symbol}, Type={self.order_Type}, Quantity={self.quantity}, Direction={self.direction}"
        )


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
        direction,
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
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """

        self.type = "FILL"
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API, in USD.

        This does not include exchange or ECN fees.

        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:  # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost
