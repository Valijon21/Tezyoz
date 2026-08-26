"""
Unit tests for TypeMaster BarChart canvas component.
Verifies canvas initialization, scaling properties, empty state triggers, duration formatting and data parsing.
"""
import unittest
import tkinter as tk
from charts.bar_chart import BarChart

class TestBarChart(unittest.TestCase):
    def setUp(self):
        # Initialize a headless Tk root to parent test widgets
        self.root = tk.Tk()
        self.root.withdraw()
        self.chart = BarChart(self.root, width=400, height=300)

    def tearDown(self):
        # Destroy and cleanup Tk resources
        self.chart.destroy()
        self.root.destroy()

    def test_initialization_defaults(self):
        """Verify constructor initializes fields and binds dimensions correctly."""
        self.assertEqual(self.chart.raw_data, [])
        self.assertEqual(self.chart.x_key, "date")
        self.assertEqual(self.chart.y_key, "practice_seconds")
        self.assertEqual(self.chart.bar_color, "#3b82f6")

    def test_duration_formatting(self):
        """Verify format duration helper formats seconds to m/s combinations correctly."""
        self.assertEqual(self.chart._format_duration(45), "45s")
        self.assertEqual(self.chart._format_duration(60), "1m")
        self.assertEqual(self.chart._format_duration(90), "1.5m")
        self.assertEqual(self.chart._format_duration(120), "2m")
        self.assertEqual(self.chart._format_duration(150), "2.5m")

    def test_empty_state_rendering(self):
        """Verify empty datasets render friendly offline text notice."""
        self.chart.set_data([])
        self.chart.update()
        
        items = self.chart.find_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.chart.type(items[0]), "text")
        self.assertEqual(self.chart.itemcget(items[0], "text"), "Natijalar mavjud emas")

    def test_set_valuable_data_points_draws_bars_and_labels(self):
        """Verify passing chronological data computes coordinates and prints canvas elements."""
        mock_data = [
            {"date": "2026-08-20", "practice_seconds": 45.0},
            {"date": "2026-08-21", "practice_seconds": 120.0},
            {"date": "2026-08-22", "practice_seconds": 90.0}
        ]
        self.chart.set_data(mock_data)
        self.chart.update()
        
        # Verify elements are populated
        all_elements = self.chart.find_all()
        self.assertTrue(len(all_elements) > 0)
        
        # Find rect bars tags (using find_withtag with "plot_bar")
        bar_elements = self.chart.find_withtag("plot_bar")
        self.assertEqual(len(bar_elements), 3)
        for bar in bar_elements:
            self.assertEqual(self.chart.type(bar), "rectangle")

    def test_clear_deletes_components(self):
        """Verify clear cleans internal list lists and deletes canvas layout."""
        mock_data = [{"date": "2026-08-20", "practice_seconds": 45.0}]
        self.chart.set_data(mock_data)
        self.chart.update()
        self.assertTrue(len(self.chart.find_all()) > 0)
        
        self.chart.clear()
        self.assertEqual(self.chart.raw_data, [])
        self.assertEqual(len(self.chart.find_all()), 0)

if __name__ == '__main__':
    unittest.main()
