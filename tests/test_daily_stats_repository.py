"""
Unit tests for TypeMaster DailyStatsRepository.
Verifies aggregation, default fallback configurations, record upserts and calculations correctness.
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.connection import db
from database.schema import initialize_schema
from database.repositories.test_repository import TestRepository
from database.repositories.daily_stats_repository import DailyStatsRepository

class TestDailyStatsRepository(unittest.TestCase):
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

        # Insert a mock user to satisfy foreign key constraint mapping
        query = """
            INSERT INTO users (username, display_name, password_hash)
            VALUES (?, ?, ?)
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, ("tester_stats", "Stats User", "dummyhash"))
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

    def test_get_daily_stats_empty_fallback(self):
        """Verify get_daily_stats yields fallback zero metrics when database contains no record."""
        stats = self.stats_repo.get_daily_stats(self.user_id, "2026-08-26")
        self.assertEqual(stats["tests_count"], 0)
        self.assertEqual(stats["practice_seconds"], 0)
        self.assertEqual(stats["average_wpm"], 0.0)
        self.assertEqual(stats["best_wpm"], 0.0)
        self.assertEqual(stats["average_accuracy"], 0.0)
        self.assertEqual(stats["best_accuracy"], 0.0)
        self.assertEqual(stats["total_characters"], 0)
        self.assertEqual(stats["total_errors"], 0)
        self.assertEqual(stats["xp_earned"], 0)

    def test_update_daily_stats_aggregates_properly(self):
        """Verify update_daily_stats correctly calculates WPM limits, accuracy percentages, counts, and sums."""
        # Insert test 1: 15s duration, 50 WPM, 90% Acc, 50 Char, 5 Errors, 15 XP
        self.test_repo.save_test(
            user_id=self.user_id, mode="15s", duration=15, language="English",
            wpm=50.0, raw_wpm=52.0, accuracy=90.0, characters=50,
            correct_characters=45, incorrect_characters=5,
            completed_at="2026-08-26 10:00:00", xp_earned=15
        )

        # Insert test 2: 30s duration, 60 WPM, 100% Acc, 100 Char, 0 Errors, 25 XP
        self.test_repo.save_test(
            user_id=self.user_id, mode="30s", duration=30, language="English",
            wpm=60.0, raw_wpm=60.0, accuracy=100.0, characters=100,
            correct_characters=100, incorrect_characters=0,
            completed_at="2026-08-26 12:00:00", xp_earned=25
        )

        # Perform stats aggregation update
        stats = self.stats_repo.update_daily_stats(self.user_id, "2026-08-26")
        
        # Verify result values matches exactly
        self.assertEqual(stats["tests_count"], 2)
        self.assertEqual(stats["practice_seconds"], 45) # 15 + 30
        self.assertEqual(stats["average_wpm"], 55.0) # (50 + 60) / 2
        self.assertEqual(stats["best_wpm"], 60.0) # Max WPM
        self.assertEqual(stats["average_accuracy"], 95.0) # (90 + 100) / 2
        self.assertEqual(stats["best_accuracy"], 100.0) # Max Acc
        self.assertEqual(stats["total_characters"], 150) # 50 + 100
        self.assertEqual(stats["total_errors"], 5) # 5 + 0
        self.assertEqual(stats["xp_earned"], 40) # 15 + 25

        # Double check DB got updated
        db_stats = self.stats_repo.get_daily_stats(self.user_id, "2026-08-26")
        self.assertEqual(db_stats["tests_count"], 2)
        self.assertEqual(db_stats["practice_seconds"], 45)

    def test_update_daily_stats_conflict_upsert(self):
        """Verify subsequent updates on same day overrides and updates daily_stats records correctly without duplicates."""
        # Insert test 1
        self.test_repo.save_test(
            user_id=self.user_id, mode="15s", duration=15, language="English",
            wpm=50.0, raw_wpm=50.0, accuracy=100.0, characters=50,
            correct_characters=50, incorrect_characters=0,
            completed_at="2026-08-26 10:00:00", xp_earned=10
        )
        self.stats_repo.update_daily_stats(self.user_id, "2026-08-26")

        # Insert test 2 later
        self.test_repo.save_test(
            user_id=self.user_id, mode="15s", duration=15, language="English",
            wpm=60.0, raw_wpm=60.0, accuracy=100.0, characters=50,
            correct_characters=50, incorrect_characters=0,
            completed_at="2026-08-26 15:00:00", xp_earned=15
        )
        stats = self.stats_repo.update_daily_stats(self.user_id, "2026-08-26")

        # Verify it has overridden rather than appended rows
        self.assertEqual(stats["tests_count"], 2)
        self.assertEqual(stats["xp_earned"], 25) # 10 + 15

        # Verify only one row exists in daily_stats for this user and date
        with db.transaction() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM daily_stats WHERE user_id = ? AND date = ?", (self.user_id, "2026-08-26"))
            row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, 1)

    def test_daily_growth_calculations(self):
        """Verify daily growth calculations for active days, empty fallback, and zero previous days."""
        # Case 1: Yesterday has 40 WPM, Today has 50 WPM (25% Growth)
        self.test_repo.save_test(
            self.user_id, "15s", 15, "English",
            40.0, 40.0, 100.0, 50, 50, 0,
            completed_at="2026-08-25 10:00:00", xp_earned=10
        )
        self.stats_repo.update_daily_stats(self.user_id, "2026-08-25")

        self.test_repo.save_test(
            self.user_id, "15s", 15, "English",
            50.0, 50.0, 100.0, 50, 50, 0,
            completed_at="2026-08-26 10:00:00", xp_earned=10
        )
        stats = self.stats_repo.update_daily_stats(self.user_id, "2026-08-26")

        self.assertEqual(stats["growth"], 25.0)

        # Case 2: Today has stats but Yesterday had no stats (Fallback/Zero previous, growth should be 100.0)
        self.test_repo.save_test(
            self.user_id, "15s", 15, "English",
            60.0, 60.0, 100.0, 50, 50, 0,
            completed_at="2026-08-28 10:00:00", xp_earned=10
        )
        stats_28 = self.stats_repo.update_daily_stats(self.user_id, "2026-08-28")
        self.assertEqual(stats_28["growth"], 100.0)

        # Case 3: Empty fallback today when no tests are done
        empty_stats = self.stats_repo.get_daily_stats(self.user_id, "2026-08-29")
        # 2026-08-28 had 60 WPM, 2026-08-29 has 0.0 WPM. Growth should be -100.0%
        self.assertEqual(empty_stats["growth"], -100.0)

if __name__ == '__main__':
    unittest.main()
