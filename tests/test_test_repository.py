"""
Unit tests for TypeMaster TestRepository.
Verifies save_test database persistence, constraints, and transactions.
"""
import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
from database.connection import db
from database.schema import initialize_schema
from database.repositories.test_repository import TestRepository

class TestTestRepository(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch the global db path to use our temporary DB
        self.original_db_path = db.database_path
        db.database_path = self.db_path
        
        # Initialize schema inside connection DB
        initialize_schema()
        self.repo = TestRepository()

        # Insert a mock user to satisfy foreign key constraint mapping
        query = """
            INSERT INTO users (username, display_name, password_hash)
            VALUES (?, ?, ?)
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, ("tester", "Test User", "dummyhash"))
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

    def test_save_test_success(self):
        """Verify save_test successfully writes to tests table and returns row ID."""
        test_id = self.repo.save_test(
            user_id=self.user_id,
            mode="60s",
            duration=60,
            language="English",
            wpm=55.5,
            raw_wpm=58.0,
            accuracy=95.0,
            characters=150,
            correct_characters=142,
            incorrect_characters=8,
            xp_earned=15,
            is_pb=True
        )

        self.assertGreater(test_id, 0)

        # Retrieve row from DB and verify values matches
        with db.transaction() as conn:
            cursor = conn.execute("SELECT * FROM tests WHERE id = ?", (test_id,))
            row = cursor.fetchone()
            
        self.assertIsNotNone(row)
        self.assertEqual(row["user_id"], self.user_id)
        self.assertEqual(row["mode"], "60s")
        self.assertEqual(row["duration"], 60)
        self.assertEqual(row["language"], "English")
        self.assertEqual(row["difficulty"], "normal")
        self.assertEqual(row["wpm"], 55.5)
        self.assertEqual(row["raw_wpm"], 58.0)
        self.assertEqual(row["accuracy"], 95.0)
        self.assertEqual(row["characters"], 150)
        self.assertEqual(row["correct_characters"], 142)
        self.assertEqual(row["incorrect_characters"], 8)
        self.assertEqual(row["xp_earned"], 15)
        self.assertEqual(row["is_personal_best"], 1)
        self.assertIsNotNone(row["completed_at"])

    def test_save_test_invalid_user_checks_foreign_keys(self):
        """Verify foreign key constraint error is raised for non-existing user_id."""
        # Foreign key target user 99999 does not exist
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.save_test(
                user_id=99999,
                mode="15s",
                duration=15,
                language="Uzbek",
                wpm=40.0,
                raw_wpm=40.0,
                accuracy=100.0,
                characters=50,
                correct_characters=50,
                incorrect_characters=0
            )

if __name__ == '__main__':
    unittest.main()
