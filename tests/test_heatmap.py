"""
Unit test suite verifying Keyboard Heatmap data queries and color interpolation logic.
"""
import unittest
import tempfile
import os
from pathlib import Path
import tkinter as tk
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.key_stats_repository import KeyStatsRepository
from charts.heatmap import KeyboardHeatmap

class TestKeyboardHeatmap(unittest.TestCase):
    def setUp(self):
        # 1. Setup temporary database context
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.key_repo = KeyStatsRepository()
        self.user_id = 101
        
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                (self.user_id, "heatmap_user", "hash")
            )

        # 2. Setup Tk root for testing widgets
        self.root = tk.Tk()

    def tearDown(self):
        self.root.destroy()
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_repository_get_all_key_stats(self):
        """Verifies that KeyStatsRepository.get_all_key_stats queries all user's key records."""
        # Insert stats for key 'a' and 'b' and space
        self.key_repo.record_key_stats(self.user_id, {"a": 10, "b": 15, " ": 20}, {"a": 2, "b": 0, " ": 5})
        
        stats = self.key_repo.get_all_key_stats(self.user_id)
        
        self.assertEqual(len(stats), 3)
        self.assertIn("a", stats)
        self.assertIn("b", stats)
        self.assertIn(" ", stats)
        
        self.assertEqual(stats["a"]["attempts"], 10)
        self.assertEqual(stats["a"]["errors"], 2)
        self.assertEqual(stats["b"]["error_rate"], 0.0)
        self.assertEqual(stats[" "]["errors"], 5)

    def test_color_interpolation_math(self):
        """Checks color interpolation helper values (green, red, yellow)."""
        widget = KeyboardHeatmap(self.root)
        
        green = widget._interpolate_color(0.0)
        red = widget._interpolate_color(1.0)
        yellow = widget._interpolate_color(0.5)
        
        # Pure start/end boundaries
        self.assertEqual(green, "#10b981")
        self.assertEqual(red, "#ef4444")
        self.assertEqual(yellow, "#f59e0b")
        
        # Test intermediate ranges
        int_low = widget._interpolate_color(0.2)
        int_high = widget._interpolate_color(0.8)
        
        # Check standard hex format
        self.assertTrue(int_low.startswith("#") and len(int_low) == 7)
        self.assertTrue(int_high.startswith("#") and len(int_high) == 7)

    def test_set_widget_data(self):
        """Checks widget's set_data layout properties when receiving stats dictionary."""
        widget = KeyboardHeatmap(self.root)
        
        data = {
            "a": {"attempts": 10, "errors": 3}, # 30% rate
            "b": {"attempts": 5, "errors": 0},  # 0% rate
            "c": {"attempts": 1, "errors": 1}   # 100% rate
        }
        
        # Should execute without errors
        widget.set_data(data)
        
        # Verify backing key coordinates mapped QWERTY properties
        self.assertIn("a", widget.keys)
        self.assertIn("b", widget.keys)
        self.assertIn(" ", widget.keys)

if __name__ == '__main__':
    unittest.main()
