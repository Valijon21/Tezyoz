"""
Unit tests for TypeMaster PersonalBestRepository queries and PersonalBestView layout.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.personal_best_repository import PersonalBestRepository
from ui.personal_best import PersonalBestView

class TestPersonalBests(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.pb_repo = PersonalBestRepository()
        
        # TK resources
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = MagicMock()
        
        self.mock_user = {
            "id": 1,
            "username": "tester",
            "display_name": "Test User"
        }

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass
        self.root.destroy()

    def test_get_all_personal_bests_returns_sorted(self):
        """Verify get_all_personal_bests queries rows and returns sorted by achieved_at DESC."""
        user_id = 99
        # Insert parent user record to satisfy FOREIGN KEY constraint
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, "testuser", "hash"))

        # Save some PBs (directly executing insertions to test query retrieval cleanly)
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO personal_bests (user_id, mode, duration, best_wpm, best_accuracy, achieved_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, "words", 30, 48.0, 95.0, "2026-08-26 12:00:00")
            )
            conn.execute(
                "INSERT INTO personal_bests (user_id, mode, duration, best_wpm, best_accuracy, achieved_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, "time", 15, 62.5, 96.0, "2026-08-26 14:00:00")
            )
            conn.execute(
                "INSERT INTO personal_bests (user_id, mode, duration, best_wpm, best_accuracy, achieved_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, "quotes", 60, 42.0, 92.5, "2026-08-26 13:00:00")
            )

        results = self.pb_repo.get_all_personal_bests(user_id)
        self.assertEqual(len(results), 3)
        
        # Check sorted details (14:00, then 13:00, then 12:00)
        self.assertEqual(results[0]["best_wpm"], 62.5)
        self.assertEqual(results[0]["mode"], "time")
        self.assertEqual(results[1]["best_wpm"], 42.0)
        self.assertEqual(results[1]["mode"], "quotes")
        self.assertEqual(results[2]["best_wpm"], 48.0)
        self.assertEqual(results[2]["mode"], "words")

    def test_personal_bests_view_initialization_defaults(self):
        """Verify PersonalBestView renders proper title, table headings, and navigation."""
        view = PersonalBestView(self.root, self.controller)
        self.assertEqual(view.title_label.cget("text"), "Shaxsiy Rekordlar (Personal Bests)")
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.scrollbar)
        view.destroy()

    @patch("ui.personal_best.get_current_user")
    @patch("database.repositories.personal_best_repository.PersonalBestRepository.get_all_personal_bests")
    def test_personal_bests_view_empty_state(self, mock_get_pbs, mock_get_user):
        """Verify that empty personal best list triggers warning label state and conceals list."""
        mock_get_user.return_value = self.mock_user
        mock_get_pbs.return_value = []
        
        view = PersonalBestView(self.root, self.controller)
        view.on_show()
        
        self.assertFalse(view.tree.winfo_manager())
        self.assertTrue(view.empty_label.winfo_manager())
        self.assertEqual(view.empty_label.cget("text"), "Shaxsiy rekordlar topilmadi")
        view.destroy()

    @patch("ui.personal_best.get_current_user")
    @patch("database.repositories.personal_best_repository.PersonalBestRepository.get_all_personal_bests")
    def test_personal_bests_view_populated_rows(self, mock_get_pbs, mock_get_user):
        """Verify that records population displays gold star prefixes and formats row items in table."""
        mock_get_user.return_value = self.mock_user
        mock_get_pbs.return_value = [
            {
                "mode": "words",
                "duration": 30,
                "best_wpm": 48.0,
                "best_accuracy": 95.0,
                "achieved_at": "2026-08-26 12:00:00"
            }
        ]
        
        view = PersonalBestView(self.root, self.controller)
        view.on_show()
        
        self.assertTrue(view.tree.winfo_manager())
        self.assertFalse(view.empty_label.winfo_manager())
        
        children = view.tree.get_children()
        self.assertEqual(len(children), 1)
        
        vals = view.tree.item(children[0], "values")
        self.assertEqual(vals[0], "words")
        self.assertEqual(vals[1], "30s")
        self.assertEqual(vals[2], "★ 48.0 WPM")
        self.assertEqual(vals[3], "95.0%")
        self.assertEqual(vals[4], "2026-08-26 12:00")
        view.destroy()

if __name__ == '__main__':
    unittest.main()
