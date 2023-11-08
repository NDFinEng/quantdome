from abc import ABCMeta, abstractmethod

# Backtesting Execution Handler
class SimulatedExecutionHandler():

    def execute_order(self, order):
        # This assumes all orders get filled as is, which never actually happens
        # TODO: Need to increase the complexity here
        return order