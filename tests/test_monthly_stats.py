"""
Unit tests for TypeMaster Monthly Statistics logic.
Verifies get_monthly_stats database aggregation, default fallbacks, and 30-day sequences.
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.connection import db
from database.schema import initialize_schema
from database.repositories.test_repository import TestRepository
from database.repositories.daily_stats_repository import DailyStatsRepository

class TestMonthlyStats(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch the global db path to use our temporary DB
        self.original_db_path = db.database_path
        db.database_path = self.db_path
        
        # Initialize schema inside connection DB
        initialize_schema()
        self.test_repo = TestRepository()
        self.stats_repo = DailyStatsRepository()

        # Insert a mock user
        query = """
            INSERT INTO users (username, display_name, password_hash)
            VALUES (?, ?, ?)
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, ("tester_monthly", "Monthly User", "dummyhash"))
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

    def test_monthly_stats_empty_fallback(self):
        """Verify get_monthly_stats yields fallback zero summary and dates with zero metrics when database contains no record."""
        res = self.stats_repo.get_monthly_stats(self.user_id, "2026-08-26")
        summary = res["summary"]
        days = res["days"]

        self.assertEqual(summary["tests_count"], 0)
        self.assertEqual(summary["average_wpm"], 0.0)
        self.assertEqual(len(days), 30)
        self.assertEqual(days[0]["date"], "2026-07-28") # 29 days prior to 08-26
        self.assertEqual(days[29]["date"], "2026-08-26")
        self.assertEqual(days[0]["tests_count"], 0)

    def test_monthly_stats_aggregates_multiple_days(self):
        """Verify get_monthly_stats aggregates dates within the 30-day window and ignores dates outside."""
        # Active Day 1 (Within window): 2026-08-10
        self.test_repo.save_test(
            self.user_id, "60s", 60, "English",
            50.0, 50.0, 100.0, 100, 100, 0,
            completed_at="2026-08-10 10:00:00", xp_earned=20
        )
        self.stats_repo.update_daily_stats(self.user_id, "2026-08-10")

        # Active Day 2 (Within window): 2026-08-25
        self.test_repo.save_test(
            self.user_id, "30s", 30, "English",
            60.0, 60.0, 100.0, 100, 100, 0,
            completed_at="2026-08-25 12:00:00", xp_earned=20
        )
        self.stats_repo.update_daily_stats(self.user_id, "2026-08-25")

        # Active Day 3 (Outside window - should be ignored): 2026-07-20 (37 days prior)
        self.test_repo.save_test(
            self.user_id, "15s", 15, "English",
            70.0, 70.0, 100.0, 50, 50, 0,
            completed_at="2026-07-20 10:00:00", xp_earned=15
        )
        self.stats_repo.update_daily_stats(self.user_id, "2026-07-20")

        # Request monthly stats ending on 2026-08-26 (Range: 2026-07-28 to 2026-08-26)
        res = self.stats_repo.get_monthly_stats(self.user_id, "2026-08-26")
        summary = res["summary"]
        days = res["days"]

        # Verify summary stats
        self.assertEqual(summary["tests_count"], 2)
        self.assertEqual(summary["practice_seconds"], 90) # 60 + 30
        self.assertEqual(summary["average_wpm"], 55.0) # (50 + 60) / 2
        self.assertEqual(summary["best_wpm"], 60.0) # Max
        self.assertEqual(summary["xp_earned"], 40) # 20 + 20

        # Verify days list items
        # 2026-08-10 is day 13 (2026-07-28 to 28-08 is 30 days)
        self.assertEqual(days[13]["date"], "2026-08-10")
        self.assertEqual(days[13]["tests_count"], 1)

        # Day 28 is 2026-08-25
        self.assertEqual(days[28]["date"], "2026-08-25")
        self.assertEqual(days[28]["tests_count"], 1)

        # Day 29 is 2026-08-26 (inactive day)
        self.assertEqual(days[29]["date"], "2026-08-26")
        self.assertEqual(days[29]["tests_count"], 0)

if __name__ == '__main__':
    unittest.main()
