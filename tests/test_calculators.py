"""
Unit tests for the typing math calculators module.
"""
import unittest
from engine.calculators import (
    WpmCalculator,
    RawWpmCalculator,
    AccuracyCalculator,
    ConsistencyCalculator
)

class TestCalculators(unittest.TestCase):
    def test_wpm_calculator(self):
        # Base case
        self.assertAlmostEqual(WpmCalculator.calculate(100, 60.0), 20.0)
        self.assertAlmostEqual(WpmCalculator.calculate(150, 30.0), 60.0)
        # Boundary cases: zero elapsed time
        self.assertEqual(WpmCalculator.calculate(100, 0.0), 0.0)
        self.assertEqual(WpmCalculator.calculate(100, -5.0), 0.0)

    def test_raw_wpm_calculator(self):
        # Base case
        self.assertAlmostEqual(RawWpmCalculator.calculate(120, 60.0), 24.0)
        self.assertAlmostEqual(RawWpmCalculator.calculate(200, 40.0), 60.0)
        # Boundary cases: zero elapsed time
        self.assertEqual(RawWpmCalculator.calculate(120, 0.0), 0.0)
        self.assertEqual(RawWpmCalculator.calculate(120, -10.0), 0.0)

    def test_accuracy_calculator(self):
        # Base case
        self.assertAlmostEqual(AccuracyCalculator.calculate(95, 100), 95.0)
        self.assertAlmostEqual(AccuracyCalculator.calculate(40, 50), 80.0)
        # Boundary cases: zero typed
        self.assertEqual(AccuracyCalculator.calculate(0, 0), 0.0)
        self.assertEqual(AccuracyCalculator.calculate(10, 0), 0.0)

    def test_consistency_calculator(self):
        # Base case: perfect rhythm (zero variance)
        self.assertAlmostEqual(ConsistencyCalculator.calculate([1.0, 2.0, 3.0, 4.0]), 100.0)
        
        # Insufficient keys (< 3 intervals, where intervals has len < 2)
        self.assertEqual(ConsistencyCalculator.calculate([]), 100.0)
        self.assertEqual(ConsistencyCalculator.calculate([1.0]), 100.0)
        self.assertEqual(ConsistencyCalculator.calculate([1.0, 2.0]), 100.0)
        
        # Real rhythm variance case
        # Keystrokes at 1.0, 2.2, 3.5, 4.7
        # Intervals: 1.2, 1.3, 1.2
        # Mean = 1.2333333333333334
        # Standard deviation = 0.04714045207910313
        # cv = std_dev / mean = 0.03822198817224578
        # Cons = (1.0 - 0.03822198817224578) * 100 = 96.1778%
        cons = ConsistencyCalculator.calculate([1.0, 2.2, 3.5, 4.7])
        self.assertTrue(90.0 < cons < 100.0)

        # Zero mean interval case (all timestamps identical)
        self.assertEqual(ConsistencyCalculator.calculate([1.0, 1.0, 1.0]), 0.0)

if __name__ == '__main__':
    unittest.main()
