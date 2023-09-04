import unittest
import quantdome.execution as execution  # Import your class containing the functions

class TestLatencyCalculation(unittest.TestCase):
    def setUp(self):
        self.trading_instance = execution.SimulatedExecutionHandle()  # Create an instance of your class

    def test_calculate_latency(self):
        order_quantity = 100  # Example order quantity
        expected_latency = 0.001 + (order_quantity * 0.00005)  # Expected latency calculation

        calculated_latency = self.trading_instance.calculate_latency(order_quantity)

        self.assertAlmostEqual(calculated_latency, expected_latency, places=5, msg="Latency calculation incorrect")
        
    def test_calculate_slippage(self):
        order_quantity = 100  # Example order quantity
        market_volatility = 0.01  # Example market volatility

        calculated_slippage = self.trading_instance.calculate_slippage(order_quantity, market_volatility)

        self.assertTrue(calculated_slippage >= 0, msg="Slippage should be non-negative")

    def test_calculate_market_impact(self):
        order_quantity = 100  # Example order quantity

        calculated_market_impact = self.trading_instance.calculate_market_impact(order_quantity)

        self.assertTrue(calculated_market_impact >= 0 and calculated_market_impact <= 0.01,
                        msg="Market impact should be between 0 and 0.01")

if __name__ == '__main__':
    unittest.main()