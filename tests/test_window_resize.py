"""
Unit tests for TypeMaster Window Resize layout hierarchy.
Verifies that bottom navigation frames are packed before expanding frames to prevent layout clipping.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.dashboard import DashboardView
from ui.typing_test import TypingTestView
from ui.results import ResultsView
from ui.history import HistoryView
from ui.personal_best import PersonalBestView

class TestWindowResizeLayout(unittest.TestCase):
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
        
        self.mock_user = {
            "id": 1,
            "username": "tester",
            "display_name": "Tester",
            "xp": 500,
            "level": 5,
            "current_streak": 2
        }

    def tearDown(self):
        self.patcher_settings.stop()
        self.root.destroy()

    @patch("services.auth_service.get_current_user")
    @patch("database.repositories.daily_stats_repository.DailyStatsRepository.get_daily_stats")
    def test_dashboard_view_packing_order(self, mock_get_stats, mock_get_user):
        """Verify that chart_display_frame is packed in DashboardView."""
        mock_get_user.return_value = self.mock_user
        mock_get_stats.return_value = {"days": [], "summary": {}}
        
        view = DashboardView(self.root, self.controller)
        view.on_show()
        
        slaves = view.container.pack_slaves()
        self.assertIn(view.chart_display_frame, slaves)

    @patch("services.auth_service.get_current_user")
    def test_typing_test_view_packing_order(self, mock_get_user):
        """Verify that button_frame and info_lbl are packed before canvas_frame in TypingTestView."""
        mock_get_user.return_value = self.mock_user
        
        view = TypingTestView(self.root, self.controller)
        
        slaves = view.container.pack_slaves()
        self.assertIn(view.button_frame, slaves)
        self.assertIn(view.info_lbl, slaves)
        self.assertIn(view.canvas_frame, slaves)
        
        btn_index = slaves.index(view.button_frame)
        info_index = slaves.index(view.info_lbl)
        canvas_index = slaves.index(view.canvas_frame)
        
        self.assertLess(btn_index, canvas_index, "button_frame should be packed before canvas_frame")
        self.assertLess(info_index, canvas_index, "info_lbl should be packed before canvas_frame")

    def test_results_view_packing_order(self):
        """Verify that database buttons_frame is packed before metrics_frame in ResultsView."""
        view = ResultsView(self.root, self.controller)
        
        slaves = view.container.pack_slaves()
        self.assertIn(view.buttons_frame, slaves)
        self.assertIn(view.metrics_frame, slaves)
        
        btn_index = slaves.index(view.buttons_frame)
        metrics_index = slaves.index(view.metrics_frame)
        self.assertLess(btn_index, metrics_index, "buttons_frame should be packed before metrics_frame")

    @patch("services.auth_service.get_current_user")
    @patch("database.repositories.test_repository.TestRepository.get_tests_by_user")
    def test_history_view_packing_order(self, mock_get_tests, mock_get_user):
        """Verify that nav_bar is packed before table_frame in HistoryView."""
        mock_get_user.return_value = self.mock_user
        mock_get_tests.return_value = []
        
        view = HistoryView(self.root, self.controller)
        view.on_show()
        
        slaves = view.container.pack_slaves()
        self.assertIn(view.nav_bar, slaves)
        self.assertIn(view.table_frame, slaves)
        
        nav_index = slaves.index(view.nav_bar)
        table_index = slaves.index(view.table_frame)
        self.assertLess(nav_index, table_index, "nav_bar should be packed before table_frame")

    @patch("services.auth_service.get_current_user")
    @patch("database.repositories.personal_best_repository.PersonalBestRepository.get_all_personal_bests")
    def test_personal_best_view_packing_order(self, mock_get_pb, mock_get_user):
        """Verify that nav_bar is packed before table_frame in PersonalBestView."""
        mock_get_user.return_value = self.mock_user
        mock_get_pb.return_value = []
        
        view = PersonalBestView(self.root, self.controller)
        view.on_show()
        
        slaves = view.container.pack_slaves()
        self.assertIn(view.nav_bar, slaves)
        self.assertIn(view.table_frame, slaves)
        
        nav_index = slaves.index(view.nav_bar)
        table_index = slaves.index(view.table_frame)
        self.assertLess(nav_index, table_index, "nav_bar should be packed before table_frame")
