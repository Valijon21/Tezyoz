"""
Unit tests for TypeMaster Test History queries and HistoryView layout screen.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.test_repository import TestRepository
from ui.history import HistoryView

class TestHistory(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.test_repo = TestRepository()
        
        # TK resources
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = MagicMock()
        
        self.mock_user = {
            "id": 1,
            "username": "testuser",
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

    def test_get_tests_by_user_returns_results_sorted(self):
        """Verify get_tests_by_user executes SQL and returns results sorted by completed_at DESC."""
        user_id = 99
        # Insert parent user record to satisfy FOREIGN KEY constraint
        with connection.db.transaction() as conn:
            conn.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, "testuser", "hash"))

        # Save 3 tests chronologically
        self.test_repo.save_test(user_id, "words", 30, "uz", 45.0, 50.0, 95.0, 220, 210, 10, completed_at="2026-08-26 12:00:00")
        self.test_repo.save_test(user_id, "words", 30, "uz", 65.0, 70.0, 97.0, 320, 310, 10, completed_at="2026-08-26 14:00:00")
        self.test_repo.save_test(user_id, "words", 30, "uz", 55.0, 60.0, 96.0, 270, 260, 10, completed_at="2026-08-26 13:00:00")
        
        results = self.test_repo.get_tests_by_user(user_id)
        self.assertEqual(len(results), 3)
        
        # Checking descending sequence: 14:00 first, 13:00 second, 12:00 third
        self.assertEqual(results[0]["completed_at"], "2026-08-26 14:00:00")
        self.assertEqual(results[1]["completed_at"], "2026-08-26 13:00:00")
        self.assertEqual(results[2]["completed_at"], "2026-08-26 12:00:00")
        
        self.assertEqual(results[0]["wpm"], 65.0)
        self.assertEqual(results[1]["wpm"], 55.0)
        self.assertEqual(results[2]["wpm"], 45.0)

    def test_history_view_initialization_defaults(self):
        """Verify HistoryView renders title header, scrollbar, treeview structure."""
        view = HistoryView(self.root, self.controller)
        self.assertEqual(view.title_label.cget("text"), "Mashqlar Tarixi")
        self.assertIsNotNone(view.tree)
        self.assertIsNotNone(view.scrollbar)
        view.destroy()

    @patch("ui.history.get_current_user")
    @patch("database.repositories.test_repository.TestRepository.get_tests_by_user")
    def test_history_view_empty_state(self, mock_get_tests, mock_get_user):
        """Verify that empty test histories pack correct warning label and unpack treeview."""
        mock_get_user.return_value = self.mock_user
        mock_get_tests.return_value = []
        
        view = HistoryView(self.root, self.controller)
        view.on_show()
        
        # Verify transition to empty
        self.assertFalse(view.tree.winfo_manager()) 
        self.assertTrue(view.empty_label.winfo_manager())
        self.assertEqual(view.empty_label.cget("text"), "Tarixiy mashqlar topilmadi")
        view.destroy()

    @patch("ui.history.get_current_user")
    @patch("database.repositories.test_repository.TestRepository.get_tests_by_user")
    def test_history_view_populated_rows(self, mock_get_tests, mock_get_user):
        """Verify that records population puts rows in treeview formatting personal bests."""
        mock_get_user.return_value = self.mock_user
        mock_get_tests.return_value = [
            {
                "completed_at": "2026-08-26 14:00:00",
                "mode": "words",
                "duration": 30,
                "wpm": 65.0,
                "accuracy": 97.0,
                "xp_earned": 15,
                "is_personal_best": True
            },
            {
                "completed_at": "2026-08-26 12:00:00",
                "mode": "time",
                "duration": 15,
                "wpm": 55.0,
                "accuracy": 96.0,
                "xp_earned": 10,
                "is_personal_best": False
            }
        ]
        
        view = HistoryView(self.root, self.controller)
        view.on_show()
        
        # Verify table widgets are packed visible
        self.assertTrue(view.tree.winfo_manager())
        self.assertFalse(view.empty_label.winfo_manager())
        
        children = view.tree.get_children()
        self.assertEqual(len(children), 2)
        
        from services.i18n_service import t
        # Check first item: personal best (should have star prefix value)
        val1 = view.tree.item(children[0], "values")
        self.assertEqual(val1[0], "2026-08-26 14:00")
        self.assertEqual(val1[1], t("mode_words"))
        self.assertEqual(val1[2], "30s")
        self.assertEqual(val1[3], "★ 65.0")
        self.assertEqual(val1[4], "97.0%")
        self.assertEqual(val1[5], "+15 XP")
        
        # Check second item: normal
        val2 = view.tree.item(children[1], "values")
        self.assertEqual(val2[0], "2026-08-26 12:00")
        self.assertEqual(val2[1], t("mode_time"))
        self.assertEqual(val2[3], "55.0")
        self.assertNotIn("★", val2[3])
        view.destroy()

    def test_get_tests_by_user_with_mode_filter(self):
        """Verify get_tests_by_user filters results correctly by mode."""
        user_id = 99
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, "testuser", "hash"))
            
        self.test_repo.save_test(user_id, "words", 30, "uz", 45.0, 50.0, 95.0, 220, 210, 10)
        self.test_repo.save_test(user_id, "time", 15, "uz", 65.0, 70.0, 97.0, 320, 310, 10)
        
        # Query with mode="words"
        results = self.test_repo.get_tests_by_user(user_id, mode="words")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["mode"], "words")

    def test_get_tests_by_user_with_difficulty_filter(self):
        """Verify get_tests_by_user filters results correctly by difficulty."""
        user_id = 99
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, "testuser", "hash"))
            
        self.test_repo.save_test(user_id, "words", 30, "uz", 45.0, 50.0, 95.0, 220, 210, 10, difficulty="normal")
        self.test_repo.save_test(user_id, "words", 30, "uz", 65.0, 70.0, 97.0, 320, 310, 10, difficulty="expert")
        
        # Query with difficulty="expert"
        results = self.test_repo.get_tests_by_user(user_id, difficulty="expert")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["difficulty"], "expert")

    def test_get_tests_by_user_with_only_pb_filter(self):
        """Verify get_tests_by_user filters results correctly by is_personal_best."""
        user_id = 99
        with connection.db.transaction() as conn:
            conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash) VALUES (?, ?, ?)", (user_id, "testuser", "hash"))
            
        self.test_repo.save_test(user_id, "words", 30, "uz", 45.0, 50.0, 95.0, 220, 210, 10, is_pb=True)
        self.test_repo.save_test(user_id, "words", 30, "uz", 65.0, 70.0, 97.0, 320, 310, 10, is_pb=False)
        
        # Query with only_pb=True
        results = self.test_repo.get_tests_by_user(user_id, only_pb=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["is_personal_best"], 1)

    @patch("ui.history.get_current_user")
    @patch("database.repositories.test_repository.TestRepository.get_tests_by_user")
    def test_history_view_filter_triggers_reload(self, mock_get_tests, mock_get_user):
        """Verify that UI controls modification triggers repository reload with filters."""
        mock_get_user.return_value = self.mock_user
        mock_get_tests.return_value = []
        
        view = HistoryView(self.root, self.controller)
        view.on_show() # Initial reload
        
        # Change category combo selection
        view.mode_combo.set("words")
        # Trigger combobox event manually
        view.mode_combo.event_generate("<<ComboboxSelected>>")
        mock_get_tests.assert_called_with(
            user_id=self.mock_user["id"],
            mode="words",
            difficulty="Barchasi",
            only_pb=False
        )
        
        # Change PB checkbox selection
        view.pb_var.set(True)
        mock_get_tests.assert_called_with(
            user_id=self.mock_user["id"],
            mode="words",
            difficulty="Barchasi",
            only_pb=True
        )
        
        view.destroy()

if __name__ == '__main__':
    unittest.main()
