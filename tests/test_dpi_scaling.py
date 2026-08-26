"""
Unit tests for TypeMaster DPI Scaling feature.
Verifies scaling factor computations and pixel converters.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.base import BaseView
from charts.line_chart import LineChart
from charts.bar_chart import BarChart
from app.application import Application

class TestDPIScaling(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = MagicMock()
        self.controller.current_theme = "dark"
        self.controller.current_font_family = "Consolas"
        self.controller.current_font_size = 14

    def tearDown(self):
        self.root.destroy()

    def test_base_view_scale_factor_calculations(self):
        """Verify scale conversion math in BaseView."""
        view = BaseView(self.root, self.controller)
        
        # Scenario 1: Standard definition (96 DPI) -> tk scaling = 1.33333333
        with patch.object(view, "tk") as mock_tk:
            mock_tk.call.return_value = "1.33333333"
            self.assertAlmostEqual(view.get_scale_factor(), 1.0, places=4)
            self.assertEqual(view.scale_px(100), 100)
            self.assertEqual(view.scale_px(260), 260)
            
        # Scenario 2: High definition (144 DPI / 150%) -> tk scaling = 2.0
        with patch.object(view, "tk") as mock_tk:
            mock_tk.call.return_value = "2.0"
            self.assertAlmostEqual(view.get_scale_factor(), 1.5, places=4)
            self.assertEqual(view.scale_px(100), 150)
            self.assertEqual(view.scale_px(260), 390)

        view.destroy()

    @patch("database.repositories.settings_repository.SettingsRepository.get_settings")
    @patch("app.application.Application._create_views")
    def test_application_window_geometry_scaling(self, mock_create_views, mock_get_settings):
        """Verify main window geometry centering adapts to computed scaling factors."""
        mock_get_settings.return_value = {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "English",
            "sound_enabled": True
        }
        
        # Patch tkinter.Tk to return a mock root widget
        with patch("tkinter.Tk") as mock_tk_class:
            mock_root = MagicMock()
            mock_tk_class.return_value = mock_root
            mock_root.tk.call.return_value = 2.0
            mock_root.winfo_screenwidth.return_value = 1920
            mock_root.winfo_screenheight.return_value = 1080
            
            # Setup a mock application window lifecycle
            app = Application()
            
            # Check that geometry scaling called with scaled values
            # standard: 900x600 -> scaled: 1350x900
            args, _ = mock_root.geometry.call_args
            geometry_str = args[0]
            self.assertTrue(geometry_str.startswith("1350x900"))

    def test_line_chart_drawing_scaling(self):
        """Verify LineChart scales line widths, dots and fonts based on dynamic DPI."""
        parent = tk.Frame(self.root)
        chart = LineChart(parent)
        
        # Test standard DPI drawing (96 DPI)
        with patch.object(chart, "get_scale_factor") as mock_scale:
            mock_scale.return_value = 1.0
            
            with patch.object(chart, "create_text") as mock_text, \
                 patch.object(chart, "create_line") as mock_line, \
                 patch.object(chart, "create_oval") as mock_oval:
                
                chart.set_data([
                    {"date": "2026-08-20", "average_wpm": 60.0},
                    {"date": "2026-08-21", "average_wpm": 65.0}
                ], x_key="date", y_key="average_wpm")
                
                # Checks line and oval dimensions (e.g. outline width, tag configs)
                # Line width should be 3
                line_calls = mock_line.call_args_list
                widths = [call[1].get("width") for call in line_calls if "width" in call[1]]
                self.assertIn(3, widths)
                
                # Oval scale width should be 1
                oval_calls = mock_oval.call_args_list
                widths = [call[1].get("width") for call in oval_calls if "width" in call[1]]
                self.assertIn(1, widths)
        
        # Test high-DPI scaling (150% scaling)
        with patch.object(chart, "get_scale_factor") as mock_scale:
            mock_scale.return_value = 1.5
            
            with patch.object(chart, "create_line") as mock_line, \
                 patch.object(chart, "create_oval") as mock_oval:
                
                chart.draw()
                # Connecting line width is scaled to 3 * 1.5 = 4
                line_calls = mock_line.call_args_list
                widths = [call[1].get("width") for call in line_calls if "width" in call[1]]
                self.assertIn(4, widths)
                
                # Dot outline width is scaled to 1.5 * 1.5 = 2
                oval_calls = mock_oval.call_args_list
                widths = [call[1].get("width") for call in oval_calls if "width" in call[1]]
                self.assertIn(2, widths)

        chart.destroy()
        parent.destroy()

    def test_bar_chart_drawing_scaling(self):
        """Verify BarChart scales bar widths and fonts based on dynamic DPI."""
        parent = tk.Frame(self.root)
        chart = BarChart(parent)
        
        with patch.object(chart, "get_scale_factor") as mock_scale:
            mock_scale.return_value = 1.5
            
            with patch.object(chart, "create_rectangle") as mock_rect, \
                 patch.object(chart, "create_text") as mock_text:
                
                chart.set_data([
                    {"date": "2026-08-20", "practice_seconds": 60.0},
                    {"date": "2026-08-21", "practice_seconds": 120.0}
                ], x_key="date", y_key="practice_seconds")
                
                # Expect font size of labels scaled (8 * 1.5 = 12)
                text_calls = mock_text.call_args_list
                font_sizes = [call[1].get("font")[1] for call in text_calls if "font" in call[1]]
                self.assertIn(12, font_sizes)

        chart.destroy()
        parent.destroy()

if __name__ == "__main__":
    unittest.main()
