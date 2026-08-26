"""
Unit tests for SettingsRepository and Application dynamic font styling updates.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.settings_repository import SettingsRepository
from app.application import Application

class TestFontSystem(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.settings_repo = SettingsRepository()
        
        # TK resources
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Seed test user settings
        self.user_id = 101
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", 
                         (self.user_id, "font_tester", "hash"))
            conn.execute(
                "INSERT OR IGNORE INTO user_settings (user_id, theme, font_family, font_size, language, sound_enabled, show_live_wpm, show_accuracy, caret_style) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, "dark", "Consolas", 14, "English", 1, 1, 1, "line")
            )

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass
        self.root.destroy()

    def test_settings_repository_read_and_update_fonts(self):
        """Verify SettingsRepository reads and updates font values correctly."""
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertIsNotNone(settings)
        self.assertEqual(settings["font_family"], "Consolas")
        self.assertEqual(settings["font_size"], 14)
        
        # Update family
        ok = self.settings_repo.update_setting(self.user_id, "font_family", "Courier New")
        self.assertTrue(ok)
        
        # Update size
        ok = self.settings_repo.update_setting(self.user_id, "font_size", 16)
        self.assertTrue(ok)
        
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertEqual(settings["font_family"], "Courier New")
        self.assertEqual(settings["font_size"], 16)

    @patch("services.auth_service.load_session_user")
    @patch("services.auth_service.get_current_user")
    def test_application_applies_font_styles(self, mock_get_current, mock_load):
        """Verify Application.apply_theme propagates font family/size changes to ttk styles."""
        mock_user = {"id": self.user_id, "username": "font_tester"}
        mock_load.return_value = mock_user
        mock_get_current.return_value = mock_user
        
        app = Application()
        
        # Test apply different font config
        app.apply_theme("dark", font_family="Courier New", font_size=18)
        self.assertEqual(app.current_font_family, "Courier New")
        self.assertEqual(app.current_font_size, 18)
        
        # Check ttk.Style settings configuration
        # "." default style config should contain our font info
        font_config = app.style.lookup(".", "font")
        self.assertIn("Courier New", font_config)
        self.assertIn("18", font_config)
        
        # Verify db persistence
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertEqual(settings["font_family"], "Courier New")
        self.assertEqual(settings["font_size"], 18)
        
        app.on_close()

    @patch("services.auth_service.load_session_user")
    @patch("services.auth_service.get_current_user")
    def test_dashboard_charts_redrawn_on_font_change(self, mock_get_current, mock_load):
        """Verify DashboardView propagates font updates to canvases."""
        mock_user = {"id": self.user_id, "username": "font_tester"}
        mock_load.return_value = mock_user
        mock_get_current.return_value = mock_user
        
        app = Application()
        app.show_view("home")
        
        dashboard = app.views["home"]
        
        # Update fonts on the application
        app.apply_theme("dark", font_family="Arial", font_size=12)
        
        # Verify custom canvases updated their font family
        self.assertEqual(dashboard.wpm_chart.font_family, "Arial")
        self.assertEqual(dashboard.acc_chart.font_family, "Arial")
        self.assertEqual(dashboard.time_chart.font_family, "Arial")
        
        app.on_close()

if __name__ == '__main__':
    unittest.main()
