"""
Unit test suite verifying key attempts, typos, error rates, and query ordering.
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.schema import initialize_schema
import database.connection as connection
from database.repositories.key_stats_repository import KeyStatsRepository
from engine.typing_engine import TypingEngine
from engine.test_config import TestConfig

class TestKeyErrorAnalytics(unittest.TestCase):
    def setUp(self):
        # Setup temporary database context
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        self.orig_db_path = connection.db.database_path
        connection.db.database_path = self.db_path
        
        initialize_schema()
        self.repo = KeyStatsRepository()
        self.user_id = 12
        
        with connection.db.transaction() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                (self.user_id, "testuser", "hash")
            )

    def tearDown(self):
        connection.db.database_path = self.orig_db_path
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_record_key_stats_inserts_and_aggregates(self):
        """Verify record_key_stats correctly inserts and accumulates on conflict."""
        # 1. Register initial tries: 'a' (5 attempts, 1 error), 'b' (10 attempts, 0 errors)
        self.repo.record_key_stats(self.user_id, {"a": 5, "b": 10}, {"a": 1})
        
        with connection.db.get_connection() as conn:
            row_a = conn.execute("SELECT attempts, errors FROM user_key_stats WHERE user_id = ? AND char_key = 'a';", (self.user_id,)).fetchone()
            row_b = conn.execute("SELECT attempts, errors FROM user_key_stats WHERE user_id = ? AND char_key = 'b';", (self.user_id,)).fetchone()
            self.assertEqual(row_a["attempts"], 5)
            self.assertEqual(row_a["errors"], 1)
            self.assertEqual(row_b["attempts"], 10)
            self.assertEqual(row_b["errors"], 0)

        # 2. Register subsequent tries: 'a' (+3 attempts, +2 errors) -> totals should accumulate
        self.repo.record_key_stats(self.user_id, {"a": 3}, {"a": 2})

        with connection.db.get_connection() as conn:
            row_a2 = conn.execute("SELECT attempts, errors FROM user_key_stats WHERE user_id = ? AND char_key = 'a';", (self.user_id,)).fetchone()
            self.assertEqual(row_a2["attempts"], 8)
            self.assertEqual(row_a2["errors"], 3)

    def test_get_top_error_keys_ordering(self):
        """Verify top error keys query returns records sorted by total mistakes descending."""
        self.repo.record_key_stats(self.user_id, {"x": 10, "y": 10, "z": 10}, {"x": 5, "y": 8, "z": 2})
        
        top_keys = self.repo.get_top_error_keys(self.user_id, limit=2)
        self.assertEqual(len(top_keys), 2)
        # 'y' has 8 errors (rank 1), 'x' has 5 errors (rank 2)
        self.assertEqual(top_keys[0]["char_key"], "y")
        self.assertEqual(top_keys[0]["errors"], 8)
        self.assertEqual(top_keys[1]["char_key"], "x")
        self.assertEqual(top_keys[1]["errors"], 5)

    def test_get_weak_keys_error_rates(self):
        """Verify weak keys query respects min_attempts threshold and ranks by error rate."""
        # 'a': 3/4 = 75% error rate (but attempts < 5, should be filtered if min_attempts=5)
        # 'b': 2/5 = 40% error rate (attempts=5)
        # 'c': 4/10 = 40% error rate (attempts=10, rank tie-breaker should favor most attempts/errors or default sorting order)
        # 'd': 5/8 = 62.5% error rate (attempts=8)
        self.repo.record_key_stats(self.user_id, {"a": 4, "b": 5, "c": 10, "d": 8}, {"a": 3, "b": 2, "c": 4, "d": 5})

        weak = self.repo.get_weak_keys(self.user_id, min_attempts=5, limit=3)
        self.assertEqual(len(weak), 3)
        
        # Rank 1: 'd' (62.5% rate)
        self.assertEqual(weak[0]["char_key"], "d")
        self.assertAlmostEqual(weak[0]["error_rate"], 62.5)

        # Rank 2: 'c' (40% rate, breaks attempts tie due to ORDER BY attempts DESC)
        self.assertEqual(weak[1]["char_key"], "c")
        self.assertAlmostEqual(weak[1]["error_rate"], 40.0)

        # Rank 3: 'b' (40% rate)
        self.assertEqual(weak[2]["char_key"], "b")

    def test_live_keystroke_error_tracking_in_typing_engine(self):
        """Verify TypingEngine populates character_errors live as typos are made."""
        config = TestConfig(duration=30, language="english")
        engine = TypingEngine(config)
        
        # Set controlled target text
        engine.target_text = "abc"
        engine.typed_text = ""
        
        # Type correct 'a'
        engine.input_character("a")
        self.assertEqual(len(engine.character_errors), 0)
        
        # Type incorrect 'x' (target was 'b')
        engine.input_character("x")
        self.assertEqual(engine.character_errors.get("b"), 1)
        
        # Backspace should not wipe the registered error
        engine.backspace()
        self.assertEqual(engine.character_errors.get("b"), 1)

if __name__ == '__main__':
    unittest.main()
