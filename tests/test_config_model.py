"""
Unit tests for TypeMaster TestConfig model.
Verifies defaults construction, valid setter updates, invalid language and duration validation.
"""
import unittest
from engine.test_config import TestConfig
from app.config import DEFAULT_LANGUAGE

class TestConfigModel(unittest.TestCase):
    def test_default_construction(self):
        """Verify new TestConfig defaults match configuration rules."""
        cfg = TestConfig()
        self.assertEqual(cfg.language, DEFAULT_LANGUAGE)
        self.assertEqual(cfg.duration, 60)

    def test_valid_setters(self):
        """Verify setting valid language and duration updates the config correctly."""
        cfg = TestConfig()
        
        cfg.language = " Russian "
        self.assertEqual(cfg.language, "Russian")
        
        cfg.duration = 15
        self.assertEqual(cfg.duration, 15)
        
        cfg.language = "uzbek"
        self.assertEqual(cfg.language, "Uzbek")
        
        cfg.duration = 120
        self.assertEqual(cfg.duration, 120)

    def test_aqlli_mashq_language(self):
        """Verify passing Aqlli Mashq 🧠 mode is accepted by TestConfig."""
        cfg = TestConfig()
        cfg.language = "Aqlli Mashq 🧠"
        self.assertEqual(cfg.language, "Aqlli Mashq 🧠")

    def test_invalid_language_raises(self):
        """Verify passing invalid language raises ValueError."""
        cfg = TestConfig()
        
        with self.assertRaises(ValueError):
            cfg.language = "Spanish"
            
        with self.assertRaises(ValueError):
            cfg.language = None
            
        with self.assertRaises(ValueError):
            cfg.language = 123

    def test_invalid_duration_raises(self):
        """Verify passing unsupported duration values (non-positive or non-numeric) raises ValueError."""
        cfg = TestConfig()
        
        with self.assertRaises(ValueError):
            cfg.duration = -10 # Non-positive duration
            
        with self.assertRaises(ValueError):
            cfg.duration = 0 # Non-positive duration
            
        with self.assertRaises(ValueError):
            cfg.duration = "invalid_str"
            
        with self.assertRaises(ValueError):
            cfg.duration = None

if __name__ == '__main__':
    unittest.main()
