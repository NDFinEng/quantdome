import pytest
import quantdome.portfolio as portfolio
import quantdome.data as data
import quantdome.event as event
import queue
import datetime

def create_naive():
    date = datetime.date(2023, 7, 12)
    events = queue.Queue()
    bars = data.HistoricCSVDataHandler(events, 'C:\\Users\\rcken\\OneDrive\\Documents\\School Work\\SIBC\\Trinitas 2023\\Infra_Code\\quantdome\\historical_csv', ['GOOG_test'])
    return portfolio.NaivePortfolio(bars, events, date)

def test_naive_init():
    n_port = create_naive()
    assert n_port.symbol_list == ['GOOG_test']
    assert n_port.all_positions == [{'GOOG_test':0, 'datetime':n_port.start_date}]
    assert n_port.current_positions == {'GOOG_test':0}
    assert n_port.all_holdings == [{'datetime':n_port.start_date, 'cash':n_port.initial_capital, 'commission':0.0, 'total':n_port.initial_capital, 'GOOG_test':0.0}]
    assert n_port.current_holdings == {'cash':n_port.initial_capital, 'commission':0.0, 'total':n_port.initial_capital, 'GOOG_test':0.0}

def test_naive_update_time():
    '''Tests the ability to move the portfolio forwards in time.'''
    n_port = create_naive()
    assert n_port.all_positions == [{'GOOG_test':0, 'datetime':n_port.start_date}]
    n_port.bars.update_bars()
    n_port.update_timeindex(n_port.events.get())
    assert len(n_port.all_holdings) == 2

def test_naive_order():
    '''Tests the ability to receive a Signal Event and issue an Order Event'''
    n_port = create_naive()
    date = datetime.date(2023, 7, 12)
    n_port.events.put(event.SignalEvent('GOOG_test',date,'LONG',1.0))
    n_port.update_signal(n_port.events.get())
    assert not n_port.events.empty()
    order = n_port.events.get()
    assert isinstance(order, event.OrderEvent)
    assert order.symbol == 'GOOG_test'
    assert order.order_type == 'MKT'
    assert order.quantity == 100
    assert order.direction == 'BUY'

def test_naive_fill():
    '''Tests the ability to receive a fill order and update holdings and positions accordingly.'''
    n_port = create_naive()
    n_port.bars.update_bars()
    n_port.update_timeindex(n_port.events.get())
    date = datetime.date(2023, 7, 12)
    n_port.events.put(event.FillEvent(date,'GOOG_test','NYSE',100,'BUY',119.620003))
    n_port.update_fill(n_port.events.get())
    assert n_port.current_positions['GOOG_test'] == 100
    assert n_port.current_holdings['GOOG_test'] == 11962.0003
    assert n_port.current_holdings['commission'] == 0
    assert n_port.current_holdings['cash'] == n_port.initial_capital - n_port.current_holdings['GOOG_test']
    assert n_port.current_holdings['total'] == n_port.initial_capital - n_port.current_holdings['GOOG_test']

def test_naive_curve_and_summary():
    '''Tests the ability to create an equity curve dataframe and output summary stats.'''
    n_port = create_naive()
    n_port.bars.update_bars()
    n_port.update_timeindex(n_port.events.get())
    date = datetime.date(2023, 7, 12)
    n_port.events.put(event.FillEvent(date,'GOOG_test','NYSE',100,'BUY',119.620003))
    n_port.update_fill(n_port.events.get())
    n_port.bars.update_bars()
    n_port.update_timeindex(n_port.events.get())
    n_port.create_equity_curve_dataframe()
    assert n_port.equity_curve.shape == (3, 6)
    stats = n_port.output_summary_stats()
    assert stats == [('Total Return', '0.52%'), ('Sharpe Ratio', '15.87'), ('Max Drawdown', '0.00%'), ('Drawdown Duration', '0')]
