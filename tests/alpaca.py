from quantdome.data import HistoricalDBDataHandler
from datetime import datetime

events = []
dataHandler = HistoricalDBDataHandler(events, ['AAPL'])

start_date = datetime(2023, 6, 1)
end_date = datetime(2023, 6, 30)
rows = dataHandler._get_lastest_chunk(start_date, end_date)
print(len(rows))