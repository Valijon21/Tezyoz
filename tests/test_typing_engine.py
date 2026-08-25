"""
Unit tests for TypeMaster TypingEngine.
Verifies keystrokes input comparisons, accuracy, raw WPM metrics, and timer ticks.
"""
import unittest
import time
from engine.test_config import TestConfig
from engine.typing_engine import TypingEngine

class TestTypingEngine(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig("English", 60)
        self.engine = TypingEngine(self.config)
        # Mock target text to keep comparison tests predictable and fast
        self.engine.target_text = "the quick brown fox"

    def test_typing_engine_initial_state(self):
        """Verify engine properties on creation."""
        self.assertFalse(self.engine.is_active)
        self.assertFalse(self.engine.is_finished)
        self.assertEqual(self.engine.typed_text, "")
        self.assertEqual(self.engine.total_typed_count, 0)
        self.assertEqual(self.engine.error_count, 0)
        self.assertEqual(self.engine.get_accuracy(), 0.0)
        self.assertEqual(self.engine.get_wpm(), 0.0)

    def test_typing_engine_typing_starts_timer(self):
        """Verify the first key input triggers test activation and saves start timestamp."""
        self.engine.input_character("t")
        self.assertTrue(self.engine.is_active)
        self.assertIsNotNone(self.engine.start_time)
        self.assertEqual(self.engine.typed_text, "t")
        self.assertEqual(self.engine.total_typed_count, 1)

    def test_typing_engine_metrics_calculations(self):
        """Verify accurate calculation of correct chars, errors, WPM & accuracy."""
        # Target: "the quick brown fox"
        # Input: "the qU" (total 6 characters, index 5 is 'U' instead of 'u' - 1 error)
        inputs = "the qU"
        for char in inputs:
            self.engine.input_character(char)
            
        self.assertEqual(self.engine.total_typed_count, 6)
        self.assertEqual(self.engine.error_count, 1)
        self.assertEqual(self.engine.get_correct_characters_count(), 5) # "the q" matches
        
        # Accuracy: (5 / 6) * 100 = 83.333%
        self.assertAlmostEqual(self.engine.get_accuracy(), 83.333, places=2)
        
        # Mock elapsed time to 12 seconds (0.2 minutes)
        self.engine.start_time = time.time() - 12.0
        
        # WPM = (correct_chars / 5) / elapsed_minutes = (5 / 5) / 0.2 = 5.0 WPM
        self.assertAlmostEqual(self.engine.get_wpm(), 5.0, places=2)
        
        # Raw WPM = (total_typed / 5) / elapsed_minutes = (6 / 5) / 0.2 = 6.0 Raw WPM
        self.assertAlmostEqual(self.engine.get_raw_wpm(), 6.0, places=2)

    def test_typing_engine_backspace(self):
        """Verify backspace removes last typed character without decrementing raw keystrokes count."""
        self.engine.input_character("t")
        self.engine.input_character("h")
        self.engine.input_character("e")
        self.assertEqual(self.engine.typed_text, "the")
        self.assertEqual(self.engine.total_typed_count, 3)
        self.assertEqual(self.engine.error_count, 0)
        
        # Deleting 'e'
        self.engine.backspace()
        self.assertEqual(self.engine.typed_text, "th")
        # Keystrokes count remains 3! (it tracks raw clicks)
        self.assertEqual(self.engine.total_typed_count, 3)
        
        # Retyping 'x' (incorrect: expected 'e')
        self.engine.input_character("x")
        self.assertEqual(self.engine.typed_text, "thx")
        self.assertEqual(self.engine.total_typed_count, 4)
        self.assertEqual(self.engine.error_count, 1)

    def test_typing_engine_timer_tick_completion(self):
        """Verify tick method completes the test context if duration runs out."""
        self.engine.input_character("t")
        self.assertTrue(self.engine.is_active)
        
        # Mock elapsed time past duration
        self.engine.start_time = time.time() - 65.0 # duration is 60s
        self.engine.tick()
        
        self.assertFalse(self.engine.is_active)
        self.assertTrue(self.engine.is_finished)
        self.assertIsNotNone(self.engine.end_time)

    def test_typing_engine_callbacks_trigger(self):
        """Verify callbacks lists are executed on character inputs and backspaced edits."""
        called_count = 0
        def test_callback(eng):
            nonlocal called_count
            called_count += 1
            
        self.engine.add_callback(test_callback)
        self.engine.input_character("t") # Starts test, triggers callback (1)
        self.engine.input_character("h") # Triggers callback (2)
        self.engine.backspace()           # Triggers callback (3)
        
        self.assertEqual(called_count, 3)

if __name__ == '__main__':
    unittest.main()
