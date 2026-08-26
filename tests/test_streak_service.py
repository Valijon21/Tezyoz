"""
Unit tests for TypeMaster StreakService.
Verifies date increments, breaks, redundant updates inside the same day, and longest streak preservation.
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.connection import db
from database.schema import initialize_schema
from services.streak_service import StreakService

class TestStreakService(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch the global db path to use our temporary DB
        self.original_db_path = db.database_path
        db.database_path = self.db_path
        
        # Initialize schema inside connection DB
        initialize_schema()
        self.service = StreakService()

        # Insert a mock user to satisfy foreign key constraint mapping
        query = """
            INSERT INTO users (username, display_name, password_hash, current_streak, longest_streak, last_active_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, ("tester_streak", "Streak User", "dummyhash", 0, 0, None))
            self.user_id = cursor.lastrowid

    def tearDown(self):
        # Restore original path
        db.database_path = self.original_db_path
        
        # Close file descriptor and remove temporary database file
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_streak_first_active_day(self):
        """Verify first ever active test sets streak to 1."""
        res = self.service.update_streak(self.user_id, today_str="2026-08-20")
        self.assertEqual(res["current_streak"], 1)
        self.assertEqual(res["longest_streak"], 1)
        self.assertEqual(res["last_active_date"], "2026-08-20")

    def test_streak_continuation_consecutive_days(self):
        """Verify streak increments when practicing on consecutive days."""
        # Day 1
        self.service.update_streak(self.user_id, today_str="2026-08-20")
        
        # Day 2 (Consecutive)
        res = self.service.update_streak(self.user_id, today_str="2026-08-21")
        self.assertEqual(res["current_streak"], 2)
        self.assertEqual(res["longest_streak"], 2)
        self.assertEqual(res["last_active_date"], "2026-08-21")

        # Day 3 (Consecutive)
        res = self.service.update_streak(self.user_id, today_str="2026-08-22")
        self.assertEqual(res["current_streak"], 3)
        self.assertEqual(res["longest_streak"], 3)

    def test_streak_redundant_calls_same_day(self):
        """Verify multiple tests completed on the same day do not increase streak."""
        self.service.update_streak(self.user_id, today_str="2026-08-20")
        res1 = self.service.update_streak(self.user_id, today_str="2026-08-20")
        self.assertEqual(res1["current_streak"], 1)
        
        # Next consecutive day
        self.service.update_streak(self.user_id, today_str="2026-08-21")
        res2 = self.service.update_streak(self.user_id, today_str="2026-08-21")
        self.assertEqual(res2["current_streak"], 2)

    def test_streak_break_resets_current_retains_longest(self):
        """Verify gap between activity resets current streak, but retains longest streak record."""
        # Setup streak of 3
        self.service.update_streak(self.user_id, today_str="2026-08-20")
        self.service.update_streak(self.user_id, today_str="2026-08-21")
        self.service.update_streak(self.user_id, today_str="2026-08-22")

        # Skip a day -> practice on 2026-08-24 (non-consecutive)
        res = self.service.update_streak(self.user_id, today_str="2026-08-24")
        self.assertEqual(res["current_streak"], 1)
        self.assertEqual(res["longest_streak"], 3) # Longest remains 3
        self.assertEqual(res["last_active_date"], "2026-08-24")

if __name__ == '__main__':
    unittest.main()
