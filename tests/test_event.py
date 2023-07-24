import pytest
import datetime
import quantdome.event as event

def test_market():
    m_event = event.MarketEvent()
    assert m_event.type == "MARKET"

def test_signal():
    time = datetime.time
    s_event = event.SignalEvent('GOOG', time, 'LONG', 1.0)
    assert s_event.type == 'SIGNAL'
    assert s_event.symbol == 'GOOG'
    assert s_event.datetime == time
    assert s_event.signal_type == 'LONG'
    assert s_event.strength == 1.0

def test_order(capsys):
    o_event = event.OrderEvent('GOOG', 'MKT', 100, 'BUY')
    assert o_event.type == 'ORDER'
    assert o_event.symbol == 'GOOG'
    assert o_event.order_type == 'MKT'
    assert o_event.quantity == 100 
    assert o_event.direction == 'BUY'
    o_event.__repr__()
    captured = capsys.readouterr()
    assert captured.out == 'Order: Symbol=GOOG, Type=MKT, Quantity=100, Direction=BUY\n'

def test_fill_no_comm():
    time = datetime.time
    f_event = event.FillEvent(time, 'GOOG', 'NYSE', 100, 'BUY', 10)
    assert f_event.type == 'FILL'
    assert f_event.symbol == 'GOOG'
    assert f_event.exchange == 'NYSE'
    assert f_event.quantity == 100
    assert f_event.direction == 'BUY'
    assert f_event.fill_cost == 10
    assert f_event.commission != 0

def test_fill_comm():
    time = datetime.time
    f_event = event.FillEvent(time, 'GOOG', 'NYSE', 100, 'BUY', 10, 0.1)
    assert f_event.type == 'FILL'
    assert f_event.symbol == 'GOOG'
    assert f_event.exchange == 'NYSE'
    assert f_event.quantity == 100
    assert f_event.direction == 'BUY'
    assert f_event.fill_cost == 10
    assert f_event.commission == 0.1