from quantdome.alpaca import AlpacaExecutionHandler

handler = AlpacaExecutionHandler()
data = handler.getQuotesData()
print(data)