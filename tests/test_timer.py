"""
Unit tests for TypeMaster TypingEngine Timer logic.
Verifies get_remaining_time calculations, and input blockage after completion.
"""
import unittest
import time
from engine.test_config import TestConfig
from engine.typing_engine import TypingEngine

class TestTimer(unittest.TestCase):
    def setUp(self):
        # Configure a short duration for testing (15 seconds)
        self.config = TestConfig("English", 15)
        self.engine = TypingEngine(self.config)
        self.engine.target_text = "hello"

    def test_get_remaining_time_unstarted(self):
        """Verify remaining time equals duration before test starts."""
        self.assertEqual(self.engine.get_remaining_time(), 15.0)

    def test_get_remaining_time_active(self):
        """Verify remaining time count decreases when test is active."""
        self.engine.input_character("h")
        self.assertTrue(self.engine.is_active)
        
        # Mock class start time to represent 5 seconds elapsed
        self.engine.start_time = time.time() - 5.0
        
        # Remaining should be 15 - 5 = 10.0
        self.assertAlmostEqual(self.engine.get_remaining_time(), 10.0, places=1)

    def test_get_remaining_time_finished(self):
        """Verify remaining time is exactly 0.0 when test completed or ticked past duration."""
        self.engine.input_character("h")
        
        # Mock elapsed time past duration
        self.engine.start_time = time.time() - 20.0
        self.engine.tick()
        
        self.assertTrue(self.engine.is_finished)
        self.assertEqual(self.engine.get_remaining_time(), 0.0)

    def test_block_interaction_on_completion(self):
        """Verify adding char or backspace doesn't mutate buffers once complete."""
        self.engine.input_character("h")
        self.engine.complete_test()
        self.assertTrue(self.engine.is_finished)
        
        # Record state buffers before attempting interactions
        typed_before = self.engine.typed_text
        typed_count_before = self.engine.total_typed_count
        
        # Input character
        self.engine.input_character("e")
        self.assertEqual(self.engine.typed_text, typed_before)
        self.assertEqual(self.engine.total_typed_count, typed_count_before)
        
        # Backspace
        self.engine.backspace()
        self.assertEqual(self.engine.typed_text, typed_before)

if __name__ == '__main__':
    unittest.main()
