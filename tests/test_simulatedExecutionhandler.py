import pytest
import quantdome.execution as execution
import quantdome.event as event
import queue

def test_init():
    events = queue.Queue()
    executor = execution.SimulatedExecutionHandler(events)
    assert executor.events == events

def test_order():
    events = queue.Queue()
    executor = execution.SimulatedExecutionHandler(events)
    assert executor.events.empty()
    order = event.OrderEvent('GOOG_test', 'MKT', 100, 'BUY')
    executor.events.put(order)
    executor.execute_order(executor.events.get())
    assert isinstance(fill := executor.events.get(), event.FillEvent)
    assert fill.symbol == order.symbol
    assert fill.exchange == 'ARCA'
    assert fill.quantity == order.quantity
    assert fill.direction == order.direction

