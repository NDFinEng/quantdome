import pytest
import quantdome.data as data
import quantdome.event as event
import queue
import pandas as pd
import datetime

def create_handler():
    events = queue.Queue()
    return data.HistoricCSVDataHandler(events, 'C:\\Users\\rcken\\OneDrive\\Documents\\School Work\\SIBC\\Trinitas 2023\\Infra_Code\\quantdome\\historical_csv', ['GOOG_test'])

def specific_csv_convert():
    '''Creates simulated bars directory directly, rather than through handler.'''
    symbol_data = {'GOOG_test':pd.read_csv('C:\\Users\\rcken\\OneDrive\\Documents\\School Work\\SIBC\\Trinitas 2023\\Infra_Code\\quantdome\\historical_csv\\GOOG_test.csv',
                                           header=0, index_col=0, parse_dates=True,
                                           names=[
                                                'datetime', 'open', 'high', 
                                                'low', 'close', 'adj_close', 'volume'
                                            ])}
    symbol_data['GOOG_test'].sort_index(inplace=True)
    symbol_data['GOOG_test'] = symbol_data['GOOG_test'].reindex(method='pad')
    symbol_data['GOOG_test']['returns'] = symbol_data['GOOG_test']["adj_close"].pct_change().dropna()
    symbol_data['GOOG_test'] = symbol_data['GOOG_test'].reindex(method='pad').iterrows()
    return symbol_data

def test_historic_csv_init():
    bars = create_handler()
    assert bars.latest_symbol_data == {'GOOG_test':[]}
    assert len(bars.symbol_data) == 1

    # Create accurate csv conversion
    gen = specific_csv_convert()

    # For each datapoint in the GOOG_test history
    for d in bars.symbol_data['GOOG_test']:

        # Generate the respective datapoint in the reference dataset
        tester = next(gen['GOOG_test'])

        # For each element of that datapoint
        for idx in range(len(d)):

            # If that element has more than one value
            try:
                 # This works to avoid the fact that NaN == NaN is false
                 res = d[idx] == tester[idx]
                 num = len(res)
                 for idx2 in range(num):
                    # The only NaN == NaN should occur at the last index of the first set of values
                    if idx2 == num - 1 and idx == 1:
                        break
                    assert res[idx2]
            # If that datapoint has only one value
            except TypeError:
                assert d[idx] == tester[idx]

def test_historic_update():
    bars = create_handler()
    # simulates backtest, continually asking for new data
    while bars.continue_backtest:
        bars.update_bars()
        assert isinstance(bars.events.get(), event.MarketEvent)
        assert bars.latest_symbol_data['GOOG_test'] != []

def test_get_latest_bars():
    '''Tests data handler's get_latest_bars() function.'''
    bars = create_handler()
    assert bars.get_latest_bars('GOOG_test') == []
    bars.update_bars()
    assert bars.get_latest_bars('GOOG_test') == [('GOOG_test', datetime.datetime(2023, 7, 12, 0, 0), 119.300003, 120.959999, 119.0, 119.620003, 119.620003)]
    bars.update_bars()
    assert bars.get_latest_bars('GOOG_test') == [('GOOG_test', datetime.datetime(2023, 7, 13, 0, 0), 121.540001, 125.334999, 121.059998, 124.830002, 124.830002)]
    assert bars.get_latest_bars('GOOG_test', 2) == [('GOOG_test', datetime.datetime(2023, 7, 12, 0, 0), 119.300003, 120.959999, 119.0, 119.620003, 119.620003),
                                                    ('GOOG_test', datetime.datetime(2023, 7, 13, 0, 0), 121.540001, 125.334999, 121.059998, 124.830002, 124.830002)]
