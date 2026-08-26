"""
Unit tests for TypeMaster XP Progress Bar dashboard rendering.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.dashboard import DashboardView

class TestXPProgressBar(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.controller = MagicMock()
        self.controller.current_theme = "dark"
        self.controller.current_font_family = "Consolas"
        self.controller.current_font_size = 14
        self.controller.root = self.root
        
        self.patcher_settings = patch("database.repositories.settings_repository.SettingsRepository.get_settings")
        self.mock_get_settings = self.patcher_settings.start()
        self.mock_get_settings.return_value = {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "English",
            "sound_enabled": True
        }
        
    def tearDown(self):
        self.patcher_settings.stop()
        self.root.destroy()
        
    @patch("ui.dashboard.get_current_user")
    @patch("ui.dashboard.DailyStatsRepository")
    def test_progress_bar_guest_state(self, mock_repo_class, mock_get_user):
        """Verify progress bar state when logged in as Guest."""
        mock_get_user.return_value = None
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_weekly_stats.return_value = {"days": [], "summary": {}}
        
        view = DashboardView(self.root, self.controller)
        view.on_show()
        
        # Check instances exist
        self.assertTrue(hasattr(view, "xp_bar"))
        self.assertTrue(hasattr(view, "xp_percent_label"))
        
        # Verify guest defaults
        self.assertEqual(view.xp_bar["maximum"], 100)
        self.assertEqual(view.xp_bar["value"], 0)
        self.assertIn("0.0%", view.xp_percent_label.cget("text"))

    @patch("ui.dashboard.get_current_user")
    @patch("ui.dashboard.DailyStatsRepository")
    def test_progress_bar_user_state(self, mock_repo_class, mock_get_user):
        """Verify progress bar calculations and values when logged in with specific XP."""
        # 350 XP corresponds to Level 3, with 50 XP in level and 300 XP needed for next
        mock_get_user.return_value = {
            "id": 1,
            "username": "tester",
            "display_name": "Tester User",
            "xp": 350,
            "level": 3,
            "current_streak": 5
        }
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_weekly_stats.return_value = {"days": [], "summary": {}}
        
        view = DashboardView(self.root, self.controller)
        view.on_show()
        
        # Verify progressive values setting
        self.assertEqual(view.xp_bar["maximum"], 300)
        self.assertEqual(view.xp_bar["value"], 50)
        
        # 50 / 300 = 16.666...%
        self.assertIn("16.7%", view.xp_percent_label.cget("text"))
        self.assertIn("50/300 XP", view.xp_percent_label.cget("text"))
