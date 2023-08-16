# quantdome
Proprietary algorithmic trading and backtesting software for Notre Dame Financial Engineering

## Getting Started
To use use this code locally:

1. Install Python 3.9 or higher and a working version of Conda or [Mamba](https://mamba.readthedocs.io/en/latest/installation.html)
2. [Clone this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
3. Install project dependencies from project root with:
  ```bash
  conda env create --file requirements.yaml
  ```
4. Activate the environment and begin work:
  ```bash
  conda activate quantdome
  ```

## Running a Strategy Backtest
### 1. Creating a strategy file
Inside the [strategies folder](strategies), create a new .py file and name the file after your strategy.

Import the strategy and event classes from the quantdome folder like so:
```python
from quantdome.strategy import Strategy
from quantdome.event import SignalEvent
```

Create a new class for your strategy using the Strategy abstract base class:
```python
class ExampleStrategy(Strategy):
  ...
```

Define an [__init__](https://www.w3schools.com/python/gloss_python_class_init.asp) function that takes a bars object and an events object (a queue) as arguments and, at the very least, initializes the self.bars, .symbol_list, and .events variables:
```python
def __init__(self, bars, events):
    self.bars = bars
    self.symbol_list = self.bars.symbol_list
    self.events = events
```

Finally, write any other functions within the class that need to be called in order to generate SignalEvents. Make sure to place the SignalEvent in the events queue:
```python
signal = SignalEvent(...)
self.events.put(signal)
```

### 2. Running the backtest
Navigate to the backtest_CLI.py file under the [quantdome folder](quantdome). The only edits you may choose to make to that file (locally) are on lines 26 - 30:
```python
bars = dt.ExampleDataHandler(...)
strategy = st(bars, events) # This calls your strategy, do not edit this line
date = datetime.date(...)
port = pt.ExamplePortfolio(...)
broker = ex.ExampleExecutionHandler
```
With these lines, you can select which data handler to use (for backtests, this is most likely a historical dataset), the date to start the backtest, which portfolio to use (this affects variables like commission), and which execution handler to use (affecting variables such as slippage).

Once those choices have been made, it is now time to run the backtest. There are two ways to do this, either passing the strategy name as an command line argument or as an input to the program:
```
> python .\backtest_CLI.py ExampleStrategy
```
or
```
> python .\backtest_CLI.py
Please enter your strategy's name (without .py suffix): ExampleStrategy
```

The backtest should then run, displaying your equity curve and printing certain relevant statistics. Continue to edit the algorithm in the strategies folder, or change variables in the backtest and simply save your changes, and then rerun the backtest program.

If there are any persistent issues that you cannot find a solution for, contact [Ryan Kennedy](mailto:rkenned8@nd.edu)
