"""
Unit test suite verifying consistency calculations, standard deviation logic, and database aggregation.
"""
import unittest
import tempfile
import os
import time
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.test_repository import TestRepository
from database.repositories.daily_stats_repository import DailyStatsRepository
from engine.typing_engine import TypingEngine
from engine.test_config import TestConfig

class TestConsistencyAnalytics(unittest.TestCase):
    def setUp(self):
        # Setup temporary database context
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.test_repo = TestRepository()
        self.stats_repo = DailyStatsRepository()
        self.user_id = 99
        
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                (self.user_id, "rhythm_user", "hash")
            )

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_rhythm_engine_uniform_pace(self):
        """Verifies that perfectly timed inputs result in 100% consistency."""
        config = TestConfig(duration=30, language="english")
        engine = TypingEngine(config)
        engine.target_text = "howdy pardner"
        engine.typed_text = ""
        
        # Simulating uniform key strokes (0.2s between each keypress)
        now = time.time()
        for i in range(len(engine.target_text)):
            engine.keystroke_times.append(now + (i * 0.20))
            
        consistency = engine.get_consistency()
        # SD is essentially 0, so consistency is 100%
        self.assertAlmostEqual(consistency, 100.0, places=3)

    def test_rhythm_engine_erratic_pace(self):
        """Verifies that erratic pauses between inputs result in lower consistency."""
        config = TestConfig(duration=30, language="english")
        engine = TypingEngine(config)
        engine.target_text = "slow stop fast go"
        engine.typed_text = ""
        
        # Erratic timings (large pauses like 1.5s then quick taps like 0.05s)
        base = time.time()
        timings = [
            base,
            base + 0.1,  # 0.1s
            base + 1.6,  # 1.5s pause
            base + 1.7,  # 0.1s
            base + 3.2,  # 1.5s pause
            base + 3.25, # 0.05s
            base + 4.75, # 1.5s pause
            base + 4.8   # 0.05s
        ]
        engine.keystroke_times = timings
        
        consistency = engine.get_consistency()
        # Standard deviation of intervals [0.1, 1.5, 0.1, 1.5, 0.05, 1.5, 0.05] will be quite high,
        # CV will be high, and consistency will be much lower than 100% (typically ~20-50%)
        self.assertTrue(0.0 <= consistency < 80.0)

    def test_database_persistence_and_aggregation(self):
        """Verifies that consistency aggregates correctly in daily stats repository queries."""
        # 1. Insert 2 tests with explicit consistency scores
        # Completed today
        today_str = "2026-08-26"
        completed_today_1 = f"{today_str} 10:00:00"
        completed_today_2 = f"{today_str} 12:00:00"
        
        self.test_repo.save_test(
            user_id=self.user_id, mode="30s", duration=30, language="english",
            wpm=50.0, raw_wpm=52.0, accuracy=98.0, characters=150,
            correct_characters=147, incorrect_characters=3, completed_at=completed_today_1,
            consistency=90.0
        )
        
        self.test_repo.save_test(
            user_id=self.user_id, mode="30s", duration=30, language="english",
            wpm=60.0, raw_wpm=62.0, accuracy=96.0, characters=180,
            correct_characters=175, incorrect_characters=5, completed_at=completed_today_2,
            consistency=80.0
        )
        
        # 2. Update daily stats
        updated_stats = self.stats_repo.update_daily_stats(self.user_id, today_str)
        # Average consistency should be (90 + 80) / 2 = 85.0%
        self.assertEqual(updated_stats["average_consistency"], 85.0)

        # 3. Retrieve weekly stats and verify summary averages consistency
        weekly = self.stats_repo.get_weekly_stats(self.user_id, today_str)
        self.assertEqual(weekly["summary"]["average_consistency"], 85.0)

if __name__ == '__main__':
    unittest.main()
