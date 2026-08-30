"""
Unit test suite verifying Advanced Statistics aggregators, rankings, and daily habit detection.
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.test_repository import TestRepository

class TestAdvancedStats(unittest.TestCase):
    def setUp(self):
        # Setup temporary database context
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.test_repo = TestRepository()
        self.user_id = 222
        
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                (self.user_id, "advanced_user", "hash")
            )

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_get_advanced_stats_empty(self):
        """Verifies default values are returned when user has completed no tests."""
        stats = self.test_repo.get_advanced_stats(self.user_id)
        self.assertEqual(stats["total_tests"], 0)
        self.assertEqual(stats["avg_wpm"], 0.0)
        self.assertEqual(stats["max_wpm"], 0.0)
        self.assertEqual(stats["last_10_avg_wpm"], 0.0)
        self.assertEqual(stats["typing_rank"], "beginner")

    def test_typing_ranks_and_aggregate_math(self):
        """Verifies spelling stats math averages and typing rank tags."""
        # Insert a rapid pro test
        self.test_repo.save_test(
            user_id=self.user_id, mode="60s", duration=60, language="english",
            wpm=55.0, raw_wpm=58.0, accuracy=90.0, characters=300,
            correct_characters=270, incorrect_characters=30, consistency=85.0
        )
        
        # Insert a second test
        self.test_repo.save_test(
            user_id=self.user_id, mode="30s", duration=30, language="english",
            wpm=45.0, raw_wpm=48.0, accuracy=94.0, characters=150,
            correct_characters=141, incorrect_characters=9, consistency=75.0
        )
        
        stats = self.test_repo.get_advanced_stats(self.user_id)
        
        self.assertEqual(stats["total_tests"], 2)
        self.assertEqual(stats["avg_wpm"], 50.0) # (55 + 45)/2
        self.assertEqual(stats["max_wpm"], 55.0)
        self.assertEqual(stats["avg_accuracy"], 92.0)
        self.assertEqual(stats["avg_consistency"], 80.0)
        
        # Cumulative accuracy: total correct (270+141=411) * 100 / total chars (300+150=450) = 91.33%
        self.assertAlmostEqual(stats["cumulative_accuracy"], 91.33, places=2)
        
        # Avg WPM = 50.0 -> Pro (45 <= WPM < 65)
        self.assertEqual(stats["typing_rank"], "pro")

    def test_last_10_tests_trend(self):
        """Ensures that the 'last 10 tests' trends represent only the most recent 10 tests."""
        # Insert 12 tests, speeds 10 to 120
        # Check that last 10 trend is the average of the last (highest index/recent timestamp) 10 tests
        for i in range(1, 13):
            # completed_at increments chronologically
            completed_str = f"2026-08-26 12:00:{i:02d}"
            self.test_repo.save_test(
                user_id=self.user_id, mode="30s", duration=30, language="english",
                wpm=float(i * 10), raw_wpm=float(i * 10), accuracy=95.0, characters=100,
                correct_characters=95, incorrect_characters=5, completed_at=completed_str,
                consistency=80.0
            )
            
        stats = self.test_repo.get_advanced_stats(self.user_id)
        
        # Total is 12 tests, all-time average WPM = (10+20+...+120)/12 = 65.0
        self.assertEqual(stats["total_tests"], 12)
        self.assertEqual(stats["avg_wpm"], 65.0)
        
        # Last 10 is indices 3 to 12 (speeds 30, 40, to 120).
        # Avg = (30 + 40 + 50 + 60 + 70 + 80 + 90 + 100 + 110 + 120) / 10 = 750 / 10 = 75.0
        self.assertEqual(stats["last_10_avg_wpm"], 75.0)

    def test_time_of_day_habit(self):
        """Verifies favorite practice time of day block calculation."""
        # Insert Morning test (e.g. 08:30)
        self.test_repo.save_test(
            user_id=self.user_id, mode="60s", duration=60, language="english",
            wpm=40.0, raw_wpm=40.0, accuracy=90.0, characters=200,
            correct_characters=180, incorrect_characters=20, completed_at="2026-08-26 08:30:00"
        )
        
        # Insert Afternoon test (e.g. 14:00)
        self.test_repo.save_test(
            user_id=self.user_id, mode="60s", duration=60, language="english",
            wpm=40.0, raw_wpm=40.0, accuracy=90.0, characters=200,
            correct_characters=180, incorrect_characters=20, completed_at="2026-08-26 14:00:00"
        )
        # Insert another Afternoon test (e.g. 15:45)
        self.test_repo.save_test(
            user_id=self.user_id, mode="60s", duration=60, language="english",
            wpm=40.0, raw_wpm=40.0, accuracy=90.0, characters=200,
            correct_characters=180, incorrect_characters=20, completed_at="2026-08-26 15:45:00"
        )
        
        stats = self.test_repo.get_advanced_stats(self.user_id)
        # Most active is block "afternoon" (2 tests vs 1 morning)
        self.assertEqual(stats["time_of_day_habit"], "afternoon")

if __name__ == '__main__':
    unittest.main()
