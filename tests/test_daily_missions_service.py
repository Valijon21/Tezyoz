"""
Unit test suite verifying daily missions generation, progress checks, and XP award transactions.
"""
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.test_repository import TestRepository
from services.daily_missions_service import DailyMissionsService, TEMPLATES

class TestDailyMissionsFeatures(unittest.TestCase):
    def setUp(self):
        # TempDB and session mock setups
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.test_repo = TestRepository()
        self.missions_service = DailyMissionsService()
        
        self.user_id = 99
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash, xp, level) VALUES (?, ?, ?, ?, ?)",
                (self.user_id, "testuser", "hash", 0, 1)
            )

        self.mock_user = {
            "id": self.user_id,
            "username": "testuser",
            "display_name": "Test User",
            "xp": 0,
            "level": 1
        }
        self.today_str = "2026-08-26"

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_get_or_generate_missions_creates_three_unique_items(self):
        """Verify get_or_generate_daily_missions initializes exactly 3 unique templates."""
        missions = self.missions_service.get_or_generate_daily_missions(self.user_id, self.today_str)
        self.assertEqual(len(missions), 3)
        
        keys = [m["mission_key"] for m in missions]
        self.assertEqual(len(keys), len(set(keys))) # 3 unique keys
        for m in missions:
            self.assertEqual(m["progress"], 0)
            self.assertEqual(m["completed"], 0)

    def test_get_or_generate_missions_subsequent_calls_idempotent(self):
        """Verify subsequents daily missions requests for same user/date return the same ids."""
        first = self.missions_service.get_or_generate_daily_missions(self.user_id, self.today_str)
        second = self.missions_service.get_or_generate_daily_missions(self.user_id, self.today_str)
        
        self.assertEqual([m["id"] for m in first], [m["id"] for m in second])

    @patch("services.auth_service.refresh_current_user")
    def test_update_mission_progress_wpm_milestone(self, mock_refresh):
        """Verify completing a test exceeding 50 WPM triggers progress on wpm_50 mission."""
        # Manually seed wpm_50 into DB
        with connection.db.transaction() as conn:
            conn.execute("""
                INSERT INTO user_daily_missions (user_id, date, mission_key, title, description, progress, target, xp_reward, completed)
                VALUES (?, ?, ?, ?, ?, 0, 1, 40, 0);
            """, (self.user_id, self.today_str, "wpm_50", "Tezkor barmoqlar", "WPM Target WPM"))

        newly = self.missions_service.update_mission_progress(self.user_id, self.today_str, wpm=55.0, accuracy=90.0, duration=15)
        self.assertEqual(len(newly), 1)
        self.assertEqual(newly[0]["key"], "wpm_50")
        
        # Verify DB updates
        with connection.db.get_connection() as conn:
            mission = conn.execute("SELECT progress, completed FROM user_daily_missions WHERE id = 1;").fetchone()
            self.assertEqual(mission["progress"], 1)
            self.assertEqual(mission["completed"], 1)
            
            user = conn.execute("SELECT xp FROM users WHERE id = ?;", (self.user_id,)).fetchone()
            self.assertEqual(user["xp"], 40)
            
        mock_refresh.assert_called_once()

    @patch("services.auth_service.refresh_current_user")
    def test_update_mission_progress_cumulative_durations(self, mock_refresh):
        """Verify cumulative duration increments in active time_120 missions."""
        with connection.db.transaction() as conn:
            conn.execute("""
                INSERT INTO user_daily_missions (user_id, date, mission_key, title, description, progress, target, xp_reward, completed)
                VALUES (?, ?, ?, ?, ?, 0, 120, 50, 0);
            """, (self.user_id, self.today_str, "time_120", "Vaqt sarflovchi", "Duration mission"))

        # 1. First test: duration=30s -> progress becomes 30
        newly = self.missions_service.update_mission_progress(self.user_id, self.today_str, wpm=40.0, accuracy=90.0, duration=30)
        self.assertEqual(len(newly), 0)
        
        with connection.db.get_connection() as conn:
            m = conn.execute("SELECT progress, completed FROM user_daily_missions WHERE id = 1;").fetchone()
            self.assertEqual(m["progress"], 30)
            self.assertEqual(m["completed"], 0)

        # 2. Second test: duration=100s -> progress reaches 120 (capped at target) and completes
        newly_2 = self.missions_service.update_mission_progress(self.user_id, self.today_str, wpm=40.0, accuracy=90.0, duration=100)
        self.assertEqual(len(newly_2), 1)
        
        with connection.db.get_connection() as conn:
            m2 = conn.execute("SELECT progress, completed FROM user_daily_missions WHERE id = 1;").fetchone()
            self.assertEqual(m2["progress"], 120)
            self.assertEqual(m2["completed"], 1)

    @patch("services.auth_service.refresh_current_user")
    def test_level_up_upon_mission_completion(self, mock_refresh):
        """Verify that completing daily missions re-evaluates level based on new total user XP."""
        # Seeding high initial XP but Level = 1
        with connection.db.transaction() as conn:
            conn.execute("UPDATE users SET xp = 2000, level = 1 WHERE id = ?;", (self.user_id,))
            conn.execute("""
                INSERT INTO user_daily_missions (user_id, date, mission_key, title, description, progress, target, xp_reward, completed)
                VALUES (?, ?, ?, ?, ?, 0, 1, 50, 0);
            """, (self.user_id, self.today_str, "accuracy_100", "Mukammallik", "100 accuracy"))

        newly = self.missions_service.update_mission_progress(self.user_id, self.today_str, wpm=45.0, accuracy=100.0, duration=30)
        self.assertEqual(len(newly), 1)
        
        with connection.db.get_connection() as conn:
            user = conn.execute("SELECT xp, level FROM users WHERE id = ?;", (self.user_id,)).fetchone()
            # 2000 + 50 = 2050 XP -> Level 6
            self.assertEqual(user["xp"], 2050)
            self.assertEqual(user["level"], 6)

if __name__ == '__main__':
    unittest.main()
