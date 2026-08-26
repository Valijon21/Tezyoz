"""
Unit tests for TypeMaster PersonalBestRepository.
Verifies get_personal_best and check_and_update_pb logic (first time, PB beaten, and ignored cases).
"""
import unittest
import tempfile
import os
from pathlib import Path
from database.connection import db
from database.schema import initialize_schema
from database.repositories.personal_best_repository import PersonalBestRepository

class TestPersonalBestRepository(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch the global db path to use our temporary DB
        self.original_db_path = db.database_path
        db.database_path = self.db_path
        
        # Initialize schema inside connection DB
        initialize_schema()
        self.repo = PersonalBestRepository()

        # Insert a mock user to satisfy foreign key constraint mapping
        query = """
            INSERT INTO users (username, display_name, password_hash)
            VALUES (?, ?, ?)
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, ("tester_pb", "PB User", "dummyhash"))
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

    def test_get_pb_empty_initially(self):
        """Verify get_personal_best returns None when no records exist."""
        result = self.repo.get_personal_best(self.user_id, "30s", 30)
        self.assertIsNone(result)

    def test_check_and_update_pb_first_time(self):
        """Verify first completed test automatically records as a Personal Best."""
        is_pb = self.repo.check_and_update_pb(
            user_id=self.user_id,
            mode="30s",
            duration=30,
            wpm=50.0,
            accuracy=90.0
        )
        self.assertTrue(is_pb)

        # Retrieve and verify fields matches
        pb = self.repo.get_personal_best(self.user_id, "30s", 30)
        self.assertIsNotNone(pb)
        self.assertEqual(pb["best_wpm"], 50.0)
        self.assertEqual(pb["best_accuracy"], 90.0)

    def test_check_and_update_pb_beaten(self):
        """Verify exceeding previous WPM best updates record details."""
        # Initial PB
        self.repo.check_and_update_pb(self.user_id, "60s", 60, 45.0, 92.0)

        # Beat PB with higher WPM
        is_pb = self.repo.check_and_update_pb(self.user_id, "60s", 60, 52.0, 90.0)
        self.assertTrue(is_pb)

        # Verify DB updated
        pb = self.repo.get_personal_best(self.user_id, "60s", 60)
        self.assertEqual(pb["best_wpm"], 52.0)
        self.assertEqual(pb["best_accuracy"], 90.0)

    def test_check_and_update_pb_worse_ignored(self):
        """Verify lower WPM does not update record and returns False."""
        self.repo.check_and_update_pb(self.user_id, "60s", 60, 45.0, 92.0)

        # Lower speed test result
        is_pb = self.repo.check_and_update_pb(self.user_id, "60s", 60, 40.0, 98.0)
        self.assertFalse(is_pb)

        # Verify DB retains original PB values
        pb = self.repo.get_personal_best(self.user_id, "60s", 60)
        self.assertEqual(pb["best_wpm"], 45.0)
        self.assertEqual(pb["best_accuracy"], 92.0)

    def test_check_and_update_pb_equal_wpm_better_accuracy(self):
        """Verify equal WPM speed but higher accuracy beats PB and updates database."""
        self.repo.check_and_update_pb(self.user_id, "15s", 15, 60.0, 90.0)

        # Equal speed but improved accuracy
        is_pb = self.repo.check_and_update_pb(self.user_id, "15s", 15, 60.0, 95.0)
        self.assertTrue(is_pb)

        # Check DB values updated
        pb = self.repo.get_personal_best(self.user_id, "15s", 15)
        self.assertEqual(pb["best_wpm"], 60.0)
        self.assertEqual(pb["best_accuracy"], 95.0)

    def test_check_and_update_pb_equal_wpm_worse_accuracy_ignored(self):
        """Verify equal WPM speed but lower accuracy does not update record."""
        self.repo.check_and_update_pb(self.user_id, "15s", 15, 60.0, 90.0)

        # Equal speed but worse accuracy
        is_pb = self.repo.check_and_update_pb(self.user_id, "15s", 15, 60.0, 85.0)
        self.assertFalse(is_pb)

        # Check DB values retains original
        pb = self.repo.get_personal_best(self.user_id, "15s", 15)
        self.assertEqual(pb["best_wpm"], 60.0)
        self.assertEqual(pb["best_accuracy"], 90.0)

if __name__ == '__main__':
    unittest.main()
