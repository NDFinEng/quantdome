# events.py
# data class for events

from dataclasses import dataclass   

@dataclass
class MarketUpdate:
    timestamp: int
    symbol: str
    high: float
    low: float
    open: float
    close: float
    volume: float

@dataclass
class TradeSignal:
    timestamp: int
    symbol: str
    price: float
    quantity: int

@dataclass
class TradeOrder:
    timestamp: int
    symbol: str
    price: float
    quantity: int

@dataclass
class TradeFill:
    timestamp: int
    symbol: str
    price: float
    quantity: int

@dataclass
class PortfolioState:
    timestamp: int
    symbol: str
    quantity: int
    portfolio: str
