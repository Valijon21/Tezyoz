"""
Unit tests for TypeMaster SQLite connection manager.
Verifies connection, Row factory dictionary output, and transactional commit/rollback operations.
"""
import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
from database.connection import DatabaseConnection

class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        self.db = DatabaseConnection(self.db_path)
        
        # Create tables for testing
        with self.db.get_connection() as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);")
            conn.execute(
                "CREATE TABLE test_fk ("
                "  id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "  parent_id INTEGER, "
                "  FOREIGN KEY(parent_id) REFERENCES test_table(id)"
                ");"
            )

    def tearDown(self):
        # Close file descriptor and remove the temporary database file
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_connection_establishes(self):
        """Verify connection can be opened and query executed."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT 1;")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_foreign_keys_enabled(self):
        """Verify foreign key constraint checks are active by default."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("PRAGMA foreign_keys;")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1) # 1 means ON

    def test_row_factory_dictionary(self):
        """Verify returned rows act like dicts using row_factory = sqlite3.Row."""
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO test_table (name) VALUES ('Alpha');")
            cursor = conn.execute("SELECT name FROM test_table WHERE id = 1;")
            row = cursor.fetchone()
            self.assertIsInstance(row, sqlite3.Row)
            self.assertEqual(row['name'], 'Alpha')

    def test_transaction_commits(self):
        """Verify complete block operations are successfully committed to base."""
        with self.db.transaction() as conn:
            conn.execute("INSERT INTO test_table (name) VALUES ('Beta');")
            conn.execute("INSERT INTO test_table (name) VALUES ('Gamma');")
            
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_table;")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 2)

    def test_transaction_rolls_back(self):
        """Verify operations are completely rolled back if an exception occurs."""
        try:
            with self.db.transaction() as conn:
                conn.execute("INSERT INTO test_table (name) VALUES ('Delta');")
                # Intentionally trigger an integrity error by violating foreign key constraint
                # Since foreign_keys is ON, parent_id 999 will violate referential integrity
                conn.execute("INSERT INTO test_fk (parent_id) VALUES (999);")
        except sqlite3.IntegrityError:
            pass # Expected exception
            
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_table WHERE name = 'Delta';")
            count = cursor.fetchone()[0]
            # Delta should have been rolled back and not exist in database
            self.assertEqual(count, 0)

if __name__ == '__main__':
    unittest.main()
