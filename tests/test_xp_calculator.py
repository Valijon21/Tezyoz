"""
Unit tests for TypeMaster XP calculator logic.
Verifies base completed tests, duration scaling, accuracy milestones and PB bonuses.
"""
import unittest
from gamification.xp_calculator import calculate_test_xp

class TestXPCalculator(unittest.TestCase):
    def test_calculate_xp_base(self):
        """Verify flat base XP reward for completing a test with low accuracy (no bonuses)."""
        # Duration: 15s -> yields 15 // 15 = 1 XP
        # Base Completed: 50 XP
        # Acc: 90% -> 0 bonus XP
        # PB: False -> 0 bonus XP
        # Expected: 50 + 1 = 51 XP
        xp = calculate_test_xp(duration_seconds=15, accuracy=90.0, is_pb=False)
        self.assertEqual(xp, 51)

    def test_calculate_xp_duration_scaling(self):
        """Verify XP scales correctly based on duration seconds."""
        # 30s duration -> 30 // 15 = 2 XP. Total: 50 + 2 = 52
        self.assertEqual(calculate_test_xp(30, 90.0, False), 52)
        # 60s duration -> 60 // 15 = 4 XP. Total: 50 + 4 = 54
        self.assertEqual(calculate_test_xp(60, 90.0, False), 54)
        # 120s duration -> 120 // 15 = 8 XP. Total: 50 + 8 = 58
        self.assertEqual(calculate_test_xp(120, 90.0, False), 58)

    def test_calculate_xp_accuracy_bonuses(self):
        """Verify accuracy milestones grant correct bonus XP amounts."""
        # Accuracy >= 95% and < 98% -> grants +20 XP. Total: 50 + 1 + 20 = 71
        self.assertEqual(calculate_test_xp(15, 95.0, False), 71)
        self.assertEqual(calculate_test_xp(15, 97.9, False), 71)

        # Accuracy >= 98% -> grants +40 XP. Total: 50 + 1 + 40 = 91
        self.assertEqual(calculate_test_xp(15, 98.0, False), 91)
        self.assertEqual(calculate_test_xp(15, 100.0, False), 91)

    def test_calculate_xp_pb_bonus(self):
        """Verify Personal Best achievements grant flat +100 XP bonus."""
        # Base: 50 + 1 (duration) = 51
        # PB: True -> +100. Total: 151
        self.assertEqual(calculate_test_xp(15, 90.0, True), 151)

        # Combination of PB + Accuracy >= 98%
        # Base: 50 + 1 = 51
        # Acc >= 98% -> +40. Total: 91
        # PB: True -> +100. Total: 191
        self.assertEqual(calculate_test_xp(15, 98.0, True), 191)

if __name__ == '__main__':
    unittest.main()
