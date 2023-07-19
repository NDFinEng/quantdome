import pytest
import quantdome.portfolio as portfolio
import quantdome.data as data
import quantdome.event as event
import queue
import datetime

def create_naive():
    date = datetime.date(2023, 7, 19)
    events = queue.Queue()
    events.put(event.MarketEvent())
    events.put(event.SignalEvent('GOOG_test',date,'LONG',1.0))
    events.put(event.OrderEvent('GOOG_test','MKT',100,'BUY'))
    events.put(event.FillEvent(date,'GOOG_test','NYSE',100,'BUY',122.78))
    bars = data.HistoricCSVDataHandler(events, '/quantdome/historical_csv', ['GOOG_test'])
    return portfolio.NaivePortfolio(bars, events, date)

def test_naive_init():
    pass
