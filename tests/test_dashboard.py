"""
Unit/smoke tests for TypeMaster DashboardView panel setup and bindings.
Verifies label cards updates, streak and level header details, and period toggles.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.dashboard import DashboardView

class TestDashboardView(unittest.TestCase):
    def setUp(self):
        # Initialize a headless Tk root to parent test widgets
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = MagicMock()
        
        self.mock_user = {
            "id": 1,
            "username": "testuser",
            "display_name": "Test User",
            "xp": 600,
            "level": 4,
            "current_streak": 3,
            "longest_streak": 7
        }

    def tearDown(self):
        # Destroy root resource
        self.root.destroy()

    @patch("services.daily_missions_service.DailyMissionsService")
    @patch("ui.dashboard.get_current_user")
    @patch("ui.dashboard.DailyStatsRepository")
    def test_dashboard_initialization_and_on_show(self, mock_repo_class, mock_get_user, mock_missions_class):
        """Verify on_show fetches user details and renders summaries correctly."""
        mock_get_user.return_value = self.mock_user
        
        mock_missions = MagicMock()
        mock_missions_class.return_value = mock_missions
        mock_missions.get_or_generate_daily_missions.return_value = [
            {"title": "V1", "description": "D1", "progress": 1, "target": 3, "xp_reward": 30, "completed": 0},
            {"title": "V2", "description": "D2", "progress": 1, "target": 1, "xp_reward": 40, "completed": 1},
            {"title": "V3", "description": "D3", "progress": 0, "target": 120, "xp_reward": 50, "completed": 0}
        ]
        
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Setup mock Weekly stats returns
        mock_repo.get_weekly_stats.return_value = {
            "summary": {
                "average_wpm": 45.0,
                "average_accuracy": 96.0,
                "tests_count": 8,
                "practice_seconds": 600.0,
                "growth": 12.5
            },
            "days": [
                {"date": "2026-08-20", "average_wpm": 45.0, "average_accuracy": 96.0, "practice_seconds": 600.0, "tests_count": 8}
            ]
        }
        
        # Setup mock Daily stats returns
        mock_repo.get_daily_stats.return_value = {
            "tests_count": 8,
            "practice_seconds": 600.0,
            "average_wpm": 45.0,
            "best_wpm": 45.0,
            "average_accuracy": 96.0,
            "best_accuracy": 96.0,
            "total_characters": 500,
            "total_errors": 10,
            "xp_earned": 45
        }
        
        view = DashboardView(self.root, self.controller)
        view.on_show()
        
        # Verify user attributes are displayed in header labels
        self.assertIn("Test User", view.welcome_label.cget("text"))
        self.assertIn("3 🔥", view.gamification_label.cget("text"))
        self.assertIn("Rekord: 7 kun", view.gamification_label.cget("text"))
        self.assertIn("Bosqich: 4", view.gamification_label.cget("text"))
        
        # Verify card labels are populated from the repository summary
        self.assertEqual(view.cards["wpm"].cget("text"), "45.0 WPM")
        self.assertEqual(view.cards["accuracy"].cget("text"), "96.0%")
        self.assertEqual(view.cards["consistency"].cget("text"), "0.0%")
        self.assertEqual(view.cards["streak"].cget("text"), "3 Kun")
        
        # Verify daily goal values are populated correctly
        self.assertEqual(view.daily_goal_bar.get(), 0.45)
        self.assertEqual(view.daily_goal_label.cget("text"), "Bugungi Maqsad: 45.0% (45/100 XP)")
        
        # Verify Daily Missions UI bindings
        self.assertEqual(view.mission_cols[0]["title"].cget("text"), "V1 (+30 XP)")
        self.assertEqual(view.mission_cols[0]["desc"].cget("text"), "D1")
        self.assertEqual(view.mission_cols[0]["status"].cget("text"), "Progress: 1/3")
        
        self.assertEqual(view.mission_cols[1]["title"].cget("text"), "V2 (+40 XP)")
        self.assertEqual(view.mission_cols[1]["status"].cget("text"), "Bajarildi ✅")
        
        view.destroy()

    @patch("services.daily_missions_service.DailyMissionsService")
    @patch("ui.dashboard.get_current_user")
    @patch("ui.dashboard.DailyStatsRepository")
    def test_set_period_refreshes_stats(self, mock_repo_class, mock_get_user, mock_missions_class):
        """Verify period selector clicks trigger corresponding repository metrics calls."""
        mock_get_user.return_value = self.mock_user
        
        mock_missions = MagicMock()
        mock_missions_class.return_value = mock_missions
        mock_missions.get_or_generate_daily_missions.return_value = []
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Configure default dict returns to prevent formatting errors from MagicMock
        mock_repo.get_daily_stats.return_value = {
            "average_wpm": 40.0,
            "accuracy": 95.0,
            "tests_count": 5,
            "practice_seconds": 300.0,
            "growth": 5.0,
            "xp_earned": 20
        }
        mock_repo.get_weekly_stats.return_value = {
            "summary": {
                "average_wpm": 45.0,
                "average_accuracy": 96.0,
                "tests_count": 8,
                "practice_seconds": 600.0,
                "growth": 12.5
            },
            "days": []
        }
        mock_repo.get_monthly_stats.return_value = {
            "summary": {
                "average_wpm": 50.0,
                "average_accuracy": 97.0,
                "tests_count": 25,
                "practice_seconds": 1500.0,
                "growth": 10.0
            },
            "days": []
        }
        
        view = DashboardView(self.root, self.controller)
        view.on_show() # trigger initial weekly load
        
        # Switch to daily
        view._set_period("today")
        self.assertEqual(view.active_period, "today")
        mock_repo.get_daily_stats.assert_called()
        
        # Switch to monthly
        view._set_period("monthly")
        self.assertEqual(view.active_period, "monthly")
        mock_repo.get_monthly_stats.assert_called()
        
        view.destroy()

    @patch("services.daily_missions_service.DailyMissionsService")
    @patch("ui.dashboard.logout_user")
    @patch("ui.dashboard.get_current_user")
    def test_navigation_buttons(self, mock_get_user, mock_logout, mock_missions_class):
        """Verify action buttons execute proper redirection and session clean actions."""
        mock_get_user.return_value = self.mock_user
        
        mock_missions = MagicMock()
        mock_missions_class.return_value = mock_missions
        mock_missions.get_or_generate_daily_missions.return_value = []
        view = DashboardView(self.root, self.controller)
        
        # Click start typing test
        view._handle_start_test()
        self.controller.show_view.assert_called_with("typing_test")
        
        # Click achievements
        view._handle_achievements()
        self.controller.show_view.assert_called_with("achievements")
        
        # Click log out
        view._handle_logout()
        mock_logout.assert_called_once()
        self.controller.show_view.assert_called_with("login")
        
        view.destroy()

if __name__ == '__main__':
    unittest.main()
