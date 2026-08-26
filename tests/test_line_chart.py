"""
Unit tests for TypeMaster LineChart canvas component.
Verifies canvas initialization, scaling properties, empty state triggers and data parsing.
"""
import unittest
import tkinter as tk
from charts.line_chart import LineChart

class TestLineChart(unittest.TestCase):
    def setUp(self):
        # Initialize a headless Tk root to parent test widgets
        self.root = tk.Tk()
        self.root.withdraw()
        self.chart = LineChart(self.root, width=400, height=300)

    def tearDown(self):
        # Destroy and cleanup Tk resources
        self.chart.destroy()
        self.root.destroy()

    def test_initialization_defaults(self):
        """Verify constructor initializes fields and binds dimensions correctly."""
        self.assertEqual(self.chart.raw_data, [])
        self.assertEqual(self.chart.x_key, "date")
        self.assertEqual(self.chart.y_key, "average_wpm")

    def test_empty_state_rendering(self):
        """Verify empty datasets render friendly offline text notice."""
        self.chart.set_data([])
        self.chart.update() # Force processing of drawing
        
        items = self.chart.find_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.chart.type(items[0]), "text")
        self.assertEqual(self.chart.itemcget(items[0], "text"), "Natijalar mavjud emas")

    def test_set_valuable_data_points_draws_lines_and_dots(self):
        """Verify passing chronological data computes coordinates and prints canvas elements."""
        mock_data = [
            {"date": "2026-08-20", "average_wpm": 40.0},
            {"date": "2026-08-21", "average_wpm": 60.0},
            {"date": "2026-08-22", "average_wpm": 50.0}
        ]
        self.chart.set_data(mock_data)
        self.chart.update()
        
        # Verify elements are populated (line + ovals + text labels)
        all_elements = self.chart.find_all()
        self.assertTrue(len(all_elements) > 0)
        
        # Find plot line and dots tags
        line_elements = self.chart.find_withtag("plot_line")
        dot_elements = self.chart.find_withtag("plot_dot")
        
        self.assertEqual(len(line_elements), 1)
        self.assertEqual(len(dot_elements), 3)

    def test_clear_deletes_components(self):
        """Verify clear cleans internal list lists and deletes canvas layout."""
        mock_data = [{"date": "2026-08-20", "average_wpm": 40.0}]
        self.chart.set_data(mock_data)
        self.chart.update()
        self.assertTrue(len(self.chart.find_all()) > 0)
        
        self.chart.clear()
        self.assertEqual(self.chart.raw_data, [])
        self.assertEqual(len(self.chart.find_all()), 0)

    def test_accuracy_chart_initialization_defaults(self):
        """Verify AccuracyChart presets green line color and average_accuracy key."""
        from charts.line_chart import AccuracyChart
        chart = AccuracyChart(self.root)
        self.assertEqual(chart.y_key, "average_accuracy")
        self.assertEqual(chart.line_color, "#10b981") # Emerald Green
        chart.destroy()

    def test_accuracy_chart_y_max_capping(self):
        """Verify AccuracyChart caps y_max ceiling at 100.0 even with multiplier headroom."""
        from charts.line_chart import AccuracyChart
        chart = AccuracyChart(self.root, width=400, height=300)
        
        # 95% accuracy * 1.15 = 109.25% which should cap at 100.0
        mock_data = [{"date": "2026-08-20", "average_accuracy": 95.0}]
        chart.set_data(mock_data)
        chart.update()
        
        # Check text tags generated: the maximum tick label should be capped at 100
        text_labels = [chart.itemcget(item, "text") for item in chart.find_all() if chart.type(item) == "text"]
        self.assertIn("100", text_labels)
        chart.destroy()

if __name__ == '__main__':
    unittest.main()
