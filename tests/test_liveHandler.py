# import pytest
import quantdome.data as data
import quantdome.event as event
import queue
import pandas as pd
import datetime

def create_handler():
    events = queue.Queue()
    return data.LiveDataHandler(events, ['GOOG', 'AAPL'])

def test_live_data_handler_init():
    bars = create_handler()
    assert bars.symbol_list == ['GOOG', 'AAPL']
    assert bars.latest_symbol_data == {'GOOG':[], 'AAPL':[]}

test_live_data_handler_init()