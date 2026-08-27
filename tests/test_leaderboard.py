"""
Unit tests for TypeMaster Leaderboard view and repository rankings query.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from services.auth_service import get_leaderboard, register_user
from ui.leaderboard import LeaderboardView

class TestLeaderboardFeatures(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        
        # Populate users with distinct XP/Level configurations
        self.user_ids = []
        with connection.db.transaction() as conn:
            # User A: 500 XP, Lvl 3 (Highest)
            conn.execute(
                "INSERT INTO users (username, display_name, password_hash, xp, level) VALUES (?, ?, ?, ?, ?);",
                ("usera", "User A", "hash", 500, 3)
            )
            # User B: 300 XP, Lvl 2
            conn.execute(
                "INSERT INTO users (username, display_name, password_hash, xp, level) VALUES (?, ?, ?, ?, ?);",
                ("userb", "User B", "hash", 300, 2)
            )
            # User C: 500 XP, Lvl 2 (Same XP as A, lower Level tie-breaker)
            conn.execute(
                "INSERT INTO users (username, display_name, password_hash, xp, level) VALUES (?, ?, ?, ?, ?);",
                ("userc", "User C", "hash", 500, 2)
            )

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_get_leaderboard_sorting(self):
        """Verify get_leaderboard retrieves users sorted by XP DESC, level DESC."""
        leaderboard = get_leaderboard(limit=10)
        self.assertEqual(len(leaderboard), 3)
        
        # Expectation: User A (500XP, Lvl 3) -> User C (500XP, Lvl 2) -> User B (300XP, Lvl 2)
        self.assertEqual(leaderboard[0]["username"], "usera")
        self.assertEqual(leaderboard[1]["username"], "userc")
        self.assertEqual(leaderboard[2]["username"], "userb")

    @patch("ui.leaderboard.get_current_user")
    def test_leaderboard_view_renders_cards(self, mock_get_user):
        """Verify that LeaderboardView renders row frames correctly based on user query."""
        mock_get_user.return_value = {
            "id": 999,
            "username": "testself",
            "display_name": "Test Self",
            "xp": 100,
            "level": 1
        }
        
        root = tk.Tk()
        root.withdraw()
        controller = MagicMock()
        controller.current_theme = "dark"
        controller.current_font_family = "Consolas"
        controller.current_font_size = 14
        controller.root = root

        try:
            view = LeaderboardView(root, controller)
            view.on_show()
            
            # 3 users populated + active self user isn't in db but in list they are processed if returned.
            # get_leaderboard returns exactly the 3 users in the mock database.
            self.assertEqual(len(view.rows_list), 3)
            
            # Inspect first user card components: check if rank label text incorporates the crown emoji 👑
            first_card = view.rows_list[0]
            first_card_children = first_card.winfo_children()
            
            # Rank label is the first child (grid column 0)
            rank_lbl = first_card_children[0]
            self.assertIn("👑", rank_lbl.cget("text"))
            
            # Username label is the second child (grid column 1)
            name_lbl = first_card_children[1]
            self.assertEqual(name_lbl.cget("text"), "User A")
            
            view.destroy()
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
