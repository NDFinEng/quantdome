from .quantdome.quantdome import Quantdome
from strategies.SimpleAppleStrat import SimpleAppleStrategy

from datetime import datetime

# define variables
data = "../data/AAPL.csv"
symbol_list = ["AAPL"]
strategy = SimpleAppleStrategy(180.00, 190.00)
start_date = datetime(2018, 1, 1)
end_date = datetime(2023, 9, 1)

# set state
quantdome = Quantdome(start_date, end_date, symbol_list)
quantdome.set_data_csv(data)
quantdome.add_strategy(strategy)

# run backtest
#quantdome.run()

# generate results
#quantdome.get_results()