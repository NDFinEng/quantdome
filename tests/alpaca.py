from quantdome.data import HistoricalDBDataHandler
from datetime import datetime

events = []
start_date = datetime(2023, 6, 1)
end_date = datetime(2023, 6, 2)

dataHandler = HistoricalDBDataHandler(events, ['AAPL'], start_date, end_date)
for row in dataHandler._get_new_bar('AAPL'):
    print(row)

