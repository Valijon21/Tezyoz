"""
Unit tests for TypeMaster TypingEngine Character Comparison logic.
Verifies get_char_status and get_target_chars_statuses boundaries.
"""
import unittest
from engine.test_config import TestConfig
from engine.typing_engine import TypingEngine

class TestCharacterComparison(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig("English", 60)
        self.engine = TypingEngine(self.config)
        self.engine.target_text = "abc"

    def test_char_status_bounds(self):
        """Verify get_char_status handles invalid or out of bound indices safely by returning untyped."""
        self.assertEqual(self.engine.get_char_status(-1), "untyped")
        self.assertEqual(self.engine.get_char_status(3), "untyped")
        self.assertEqual(self.engine.get_char_status(100), "untyped")

    def test_char_status_values(self):
        """Verify correct char statuses (correct, incorrect, untyped) as input advances."""
        # Un-typed state initially
        self.assertEqual(self.engine.get_char_status(0), "untyped")
        self.assertEqual(self.engine.get_char_status(1), "untyped")

        # Type 'a' (correct key)
        self.engine.input_character("a")
        self.assertEqual(self.engine.get_char_status(0), "correct")
        self.assertEqual(self.engine.get_char_status(1), "untyped")

        # Type 'x' instead of 'b' (incorrect key)
        self.engine.input_character("x")
        self.assertEqual(self.engine.get_char_status(0), "correct")
        self.assertEqual(self.engine.get_char_status(1), "incorrect")
        self.assertEqual(self.engine.get_char_status(2), "untyped")

    def test_target_chars_statuses_list(self):
        """Verify list return matches length and elements of target text indices."""
        # Empty inputs initially
        statuses = self.engine.get_target_chars_statuses()
        self.assertEqual(statuses, ["untyped", "untyped", "untyped"])

        # Type 'a'
        self.engine.input_character("a")
        statuses = self.engine.get_target_chars_statuses()
        self.assertEqual(statuses, ["correct", "untyped", "untyped"])

        # Type 'x'
        self.engine.input_character("x")
        statuses = self.engine.get_target_chars_statuses()
        self.assertEqual(statuses, ["correct", "incorrect", "untyped"])

        # Type 'c'
        self.engine.input_character("c")
        statuses = self.engine.get_target_chars_statuses()
        self.assertEqual(statuses, ["correct", "incorrect", "correct"])

if __name__ == '__main__':
    unittest.main()
