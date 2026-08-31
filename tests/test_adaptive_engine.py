"""
Unit tests for Smart Adaptive Practice Engine (adaptive_engine.py).
"""
import unittest
from engine.adaptive_engine import get_user_weak_keys, generate_adaptive_text

class TestAdaptiveEngine(unittest.TestCase):
    def test_get_user_weak_keys_fallback(self):
        keys = get_user_weak_keys(user_id=None, language="english")
        self.assertIsInstance(keys, list)
        self.assertTrue(len(keys) > 0)
        self.assertIn("e", keys)

    def test_get_user_weak_keys_uzbek(self):
        keys = get_user_weak_keys(user_id=None, language="uzbek")
        self.assertIsInstance(keys, list)
        self.assertIn("a", keys)

    def test_get_user_weak_keys_russian(self):
        keys = get_user_weak_keys(user_id=None, language="russian")
        self.assertIsInstance(keys, list)
        self.assertIn("о", keys)

    def test_generate_adaptive_text_english(self):
        text, weak_keys = generate_adaptive_text(user_id=None, language="English", target_words_count=50)
        self.assertIsInstance(text, str)
        self.assertTrue(len(text) > 0)
        words = text.split()
        self.assertEqual(len(words), 50)
        self.assertTrue(len(weak_keys) > 0)

    def test_generate_adaptive_text_uzbek(self):
        text, weak_keys = generate_adaptive_text(user_id=None, language="Uzbek", target_words_count=40)
        self.assertIsInstance(text, str)
        words = text.split()
        self.assertEqual(len(words), 40)

    def test_generate_adaptive_text_russian(self):
        text, weak_keys = generate_adaptive_text(user_id=None, language="Russian", target_words_count=30)
        self.assertIsInstance(text, str)
        words = text.split()
        self.assertEqual(len(words), 30)

if __name__ == "__main__":
    unittest.main()
