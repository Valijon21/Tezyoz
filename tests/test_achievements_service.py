"""
Unit test suite verifying achievements unlocking logic, XP milestones, and AchievementsView UI.
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
from services.achievements_service import AchievementsService
from ui.achievements import AchievementsView

class TestAchievementsFeatures(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.test_repo = TestRepository()
        self.ach_service = AchievementsService()
        
        self.user_id = 99
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, xp, level, current_streak, longest_streak) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, "testuser", "hash", 0, 1, 0, 0)
            )

        self.mock_user = {
            "id": self.user_id,
            "username": "testuser",
            "display_name": "Test User",
            "xp": 0,
            "level": 1,
            "current_streak": 0
        }

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_get_all_achievements_initially_locked(self):
        """Verify that all default achievements are registered and locked by default."""
        achievements = self.ach_service.get_all_achievements(self.user_id)
        self.assertEqual(len(achievements), 7)
        for ach in achievements:
            self.assertIsNone(ach["unlocked_at"])

    @patch("services.auth_service.refresh_current_user")
    def test_check_and_award_first_test(self, mock_refresh):
        """Verify first test completion awards 'first_test' achievement."""
        self.test_repo.save_test(self.user_id, "words", 15, "en", 45.0, 50.0, 95.0, 100, 95, 5)
        
        newly_unlocked = self.ach_service.check_and_award_achievements(self.user_id)
        self.assertEqual(len(newly_unlocked), 1)
        self.assertEqual(newly_unlocked[0]["key"], "first_test")
        self.assertEqual(newly_unlocked[0]["xp_reward"], 50)
        
        # Check database updates
        with connection.db.get_connection() as conn:
            user_row = conn.execute("SELECT xp, level FROM users WHERE id = ?;", (self.user_id,)).fetchone()
            self.assertEqual(user_row["xp"], 50)
            self.assertEqual(user_row["level"], 1) # 50 XP is still level 1
            
        mock_refresh.assert_called_once()

    @patch("services.auth_service.refresh_current_user")
    def test_check_and_award_speed_milestones(self, mock_refresh):
        """Verify high typing speed awards 'speed_60' and 'speed_100' achievements."""
        # 1. Level up speed to 65 WPM
        self.test_repo.save_test(self.user_id, "words", 15, "en", 65.0, 70.0, 95.0, 100, 95, 5)
        newly_unlocked = self.ach_service.check_and_award_achievements(self.user_id)
        
        # Should unlock first_test AND speed_60
        self.assertEqual(len(newly_unlocked), 2)
        keys = {x["key"] for x in newly_unlocked}
        self.assertTrue("first_test" in keys)
        self.assertTrue("speed_60" in keys)
        
        # 2. Exceed 100 WPM
        self.test_repo.save_test(self.user_id, "words", 15, "en", 105.0, 110.0, 95.0, 200, 195, 5)
        newly_unlocked_2 = self.ach_service.check_and_award_achievements(self.user_id)
        
        self.assertEqual(len(newly_unlocked_2), 1)
        self.assertEqual(newly_unlocked_2[0]["key"], "speed_100")

    @patch("services.auth_service.refresh_current_user")
    def test_check_accuracy_100_milestone(self, mock_refresh):
        """Verify 100% accuracy awards accuracy_100 if exam duration is at least 30s."""
        # Duration < 30s: should not unlock accuracy_100
        self.test_repo.save_test(self.user_id, "words", 15, "en", 40.0, 40.0, 100.0, 60, 60, 0)
        newly = self.ach_service.check_and_award_achievements(self.user_id)
        self.assertNotIn("accuracy_100", {x["key"] for x in newly})
        
        # Duration >= 30s with 100% accuracy: unlocks
        self.test_repo.save_test(self.user_id, "words", 30, "en", 40.0, 40.0, 100.0, 120, 120, 0)
        newly_2 = self.ach_service.check_and_award_achievements(self.user_id)
        self.assertIn("accuracy_100", {x["key"] for x in newly_2})

    @patch("services.auth_service.refresh_current_user")
    def test_streak_milestones(self, mock_refresh):
        """Verify high streak counts award streak_3 and streak_7 achievements."""
        # Set streak to 4
        with connection.db.transaction() as conn:
            conn.execute("UPDATE users SET current_streak = 4 WHERE id = ?;", (self.user_id,))
            
        newly = self.ach_service.check_and_award_achievements(self.user_id)
        keys = {x["key"] for x in newly}
        self.assertIn("streak_3", keys)
        self.assertNotIn("streak_7", keys)

        # Set streak to 8
        with connection.db.transaction() as conn:
            conn.execute("UPDATE users SET current_streak = 8 WHERE id = ?;", (self.user_id,))
            
        newly_2 = self.ach_service.check_and_award_achievements(self.user_id)
        keys_2 = {x["key"] for x in newly_2}
        self.assertIn("streak_7", keys_2)

    @patch("services.auth_service.refresh_current_user")
    def test_level_up_recalculation(self, mock_refresh):
        """Verify that awarding achievement XP automatically levels up user in DB."""
        # High level setting trigger
        with connection.db.transaction() as conn:
            conn.execute("UPDATE users SET xp = 2000, level = 6 WHERE id = ?;", (self.user_id,))
            
        self.test_repo.save_test(self.user_id, "words", 15, "en", 45.0, 50.0, 95.0, 100, 95, 5)
        newly_unlocked = self.ach_service.check_and_award_achievements(self.user_id)
        
        self.assertEqual(len(newly_unlocked), 2) # first_test (50 XP), level_5 (150 XP) - total 200 XP added to 2000 => 2200 XP
        
        # Verify db user level
        with connection.db.get_connection() as conn:
            user_row = conn.execute("SELECT xp, level FROM users WHERE id = ?;", (self.user_id,)).fetchone()
            self.assertEqual(user_row["xp"], 2200)
            self.assertTrue(user_row["level"] >= 5)

    @patch("ui.achievements.get_current_user")
    def test_achievements_view_renders_rows(self, mock_get_user):
        """Verify that AchievementsView tree displays all rows with status tags."""
        mock_get_user.return_value = self.mock_user
        
        # Unlock first_test first in DB
        with connection.db.transaction() as conn:
            conn.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?);", (self.user_id, 1))

        root = tk.Tk()
        root.withdraw()
        controller = MagicMock()
        controller.current_theme = "dark"
        controller.current_font_family = "Consolas"
        controller.current_font_size = 14
        controller.root = root

        try:
            view = AchievementsView(root, controller)
            view.on_show()
            
            self.assertTrue(view.tree.winfo_manager())
            children = view.tree.get_children()
            self.assertEqual(len(children), 7)
            
            # Check first achievement tag (unlocked)
            first_row_tags = view.tree.item(children[0], "tags")
            self.assertIn("unlocked", first_row_tags)
            
            # Check second achievement tag (locked)
            second_row_tags = view.tree.item(children[1], "tags")
            self.assertIn("locked", second_row_tags)
            view.destroy()
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
