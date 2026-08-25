"""
Smoke test suite for TypeMaster.
Checks basic imports and configuration stability.
"""
import unittest
from pathlib import Path

class TestBootstrapAndImports(unittest.TestCase):
    def test_imports(self):
        """Verify that modular pack folders compile and import without errors."""
        try:
            import app.config as config
            import app.application as application
            import ui.base as base
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import core modules: {e}")

    def test_config_constants(self):
        """Verify app configuration constants are set to exact values."""
        from app.config import APP_NAME, APP_VERSION, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
        self.assertEqual(APP_NAME, "TypeMaster")
        self.assertEqual(APP_VERSION, "1.0.0")
        self.assertEqual(DEFAULT_WINDOW_WIDTH, 900)
        self.assertEqual(DEFAULT_WINDOW_HEIGHT, 600)

    def test_directory_creation(self):
        """Verify that base logging and data directories are created on initialization."""
        from app.config import DATA_DIR, LOG_DIR
        self.assertTrue(DATA_DIR.exists())
        self.assertTrue(LOG_DIR.exists())

    def test_extended_config_constants(self):
        """Verify extended configuration variables are present and correctly typed."""
        import app.config as config
        
        # Test default modes
        self.assertEqual(config.SUPPORTED_MODES, [15, 30, 60, 120])
        self.assertEqual(config.SUPPORTED_LANGUAGES, ["English", "Russian", "Uzbek"])
        
        # Test gamification XP rewards
        self.assertEqual(config.XP_TEST_COMPLETED, 50)
        self.assertEqual(config.XP_ACCURACY_95, 20)
        self.assertEqual(config.XP_ACCURACY_98, 40)
        self.assertEqual(config.XP_PERSONAL_BEST, 100)
        self.assertEqual(config.XP_DAILY_GOAL, 100)
        
        # Test default settings
        self.assertEqual(config.DEFAULT_THEME, "dark")
        self.assertEqual(config.DEFAULT_FONT_FAMILY, "Consolas")
        self.assertEqual(config.DEFAULT_FONT_SIZE, 14)
        self.assertEqual(config.DEFAULT_LANGUAGE, "English")
        self.assertEqual(config.DEFAULT_SOUND_ENABLED, True)
        self.assertEqual(config.DEFAULT_SHOW_LIVE_WPM, True)
        self.assertEqual(config.DEFAULT_SHOW_ACCURACY, True)
        self.assertEqual(config.DEFAULT_CARET_STYLE, "line")

if __name__ == '__main__':
    unittest.main()
