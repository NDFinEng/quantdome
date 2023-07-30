import sys
import quantdome.portfolio as port
import quantdome.data as data
import quantdome.event as ev
import importlib
import queue
import datetime

def main():
    try:
        name = sys.argv[1]
    except IndexError:
        name = input('Please enter your strategy\'s name: ')

    try:
        st = importlib.import_module("strategies.%s" % name)
    except:
        print('That name is not recognized, please try again. Remember to omit the \'.py\'')
        return
    
    events = queue.Queue()
    bars = data.HistoricCSVDataHandler(events, )

if __name__ == '__main__':
    main()