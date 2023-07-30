import sys
import quantdome.portfolio as pt
import quantdome.data as data
import quantdome.execution as ex
import queue
import datetime
import time

def main():
    # Try loading strategy name as execution argument
    try:
        name = sys.argv[1]
    except IndexError:
        name = input('Please enter your strategy\'s name: ')

    # Try importing module
    try:
        st = getattr(__import__("strategies.%s" % name, fromlist=[name]), name)
        # Equivalent to: from strategies.name import name as st
    except:
        print('That name is not recognized, please try again. Remember to omit the \'.py\'')
        return
    
    # Initialize events, datahandler, strategy, portfolio, and broker
    events = queue.Queue()
    bars = data.HistoricCSVDataHandler(events, 'C:\\Users\\rcken\\OneDrive\\Documents\\School Work\\SIBC\\Trinitas 2023\\Infra_Code\\quantdome\\historical_csv', ['GOOG_test'])
    strategy = st(bars, events)
    date = datetime.date(2023, 7, 11)
    port = pt.NativePortfolio(bars, events, date)
    broker = ex.SimulatedExecutionHandler(events)

    while True:
        if bars.continue_backtest:
            bars.update_bars()
        else:
            break

        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        strategy.calculate_signals(event)
                        port.update_timeindex(event)

                    elif event.type == 'SIGNAL':
                        port.update_signal(event)

                    elif event.type == 'ORDER':
                        broker.execute_order(event)

                    elif event.type == 'FILL':
                        port.update_fill(event)
        
        time.sleep(60)


if __name__ == '__main__':
    main()