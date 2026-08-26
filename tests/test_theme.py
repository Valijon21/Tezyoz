"""
Unit tests for SettingsRepository and Application theme styling updates.
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
from ui.theme import THEMES

class TestThemeSystem(unittest.TestCase):
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
        self.user_id = 99
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", 
                         (self.user_id, "theme_tester", "hash"))
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

    def test_settings_repository_read_and_write(self):
        """Verify SettingsRepository reads and updates database preferences correctly."""
        # Test read
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertIsNotNone(settings)
        self.assertEqual(settings["theme"], "dark")
        
        # Test update to light
        ok = self.settings_repo.update_setting(self.user_id, "theme", "light")
        self.assertTrue(ok)
        
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertEqual(settings["theme"], "light")
        
        # Test update of invalid key
        ok = self.settings_repo.update_setting(self.user_id, "invalid_column", "val")
        self.assertFalse(ok)

    @patch("services.auth_service.load_session_user")
    @patch("services.auth_service.get_current_user")
    def test_application_applies_theme_styles(self, mock_get_current_user, mock_load_user):
        """Verify Application.apply_theme changes root bg and updates ttk styles."""
        mock_user = {"id": self.user_id, "username": "theme_tester"}
        mock_load_user.return_value = mock_user
        mock_get_current_user.return_value = mock_user
        
        app = Application()
        
        # Test apply light theme
        app.apply_theme("light")
        self.assertEqual(app.current_theme, "light")
        
        # Check root background colour
        expected_bg = THEMES["light"]["bg"]
        self.assertEqual(app.root.cget("background"), expected_bg)
        
        # Check database updated
        settings = self.settings_repo.get_settings(self.user_id)
        self.assertEqual(settings["theme"], "light")
        
        # Test apply cyberpunk theme
        app.apply_theme("cyberpunk")
        self.assertEqual(app.current_theme, "cyberpunk")
        expected_cyber_bg = THEMES["cyberpunk"]["bg"]
        self.assertEqual(app.root.cget("background"), expected_cyber_bg)
        
        app.on_close()

    @patch("services.auth_service.load_session_user")
    @patch("services.auth_service.get_current_user")
    def test_dashboard_charts_redrawn_on_theme_change(self, mock_get_current, mock_load):
        """Verify DashboardView updates canvas colors on theme change."""
        mock_user = {"id": self.user_id, "username": "theme_tester"}
        mock_load.return_value = mock_user
        mock_get_current.return_value = mock_user
        
        app = Application()
        app.show_view("home")
        
        dashboard = app.views["home"]
        
        # Changing application theme propagates to dashboard charts
        app.apply_theme("cyberpunk")
        
        cyber_colors = THEMES["cyberpunk"]
        self.assertEqual(dashboard.wpm_chart.bg_color, cyber_colors["bg"])
        self.assertEqual(dashboard.acc_chart.bg_color, cyber_colors["bg"])
        self.assertEqual(dashboard.time_chart.bg_color, cyber_colors["bg"])
        
        app.on_close()

if __name__ == '__main__':
    unittest.main()
