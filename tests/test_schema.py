"""
Unit tests for TypeMaster SQLite database schema.
Verifies table creation, foreign key constraints (cascading on delete), uniqueness, and default values.
"""
import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
from database.connection import DatabaseConnection

class TestDatabaseSchema(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        self.db = DatabaseConnection(self.db_path)
        
        # Patch the schema.py global db to direct to our temporary DB
        import database.schema as schema
        self.original_db_path = schema.db.database_path
        schema.db.database_path = self.db_path
        
        # Initialize schema for test db
        schema.initialize_schema()

    def tearDown(self):
        # Restore original path
        import database.schema as schema
        schema.db.database_path = self.original_db_path
        
        # Remove temporary DB
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_schema_creates_all_tables(self):
        """Verify that all 5 required tables are created in the database."""
        expected_tables = {"users", "tests", "daily_stats", "personal_bests", "user_settings"}
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row['name'] for row in cursor.fetchall()}
            
        for table in expected_tables:
            self.assertIn(table, tables, f"Expected table '{table}' not found in database.")

    def test_unique_username_constraint(self):
        """Verify duplicate usernames cannot be inserted into the users table."""
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, display_name, password_hash) "
                "VALUES ('user1', 'User One', 'hash1');"
            )
            
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO users (username, display_name, password_hash) "
                    "VALUES ('user1', 'User Two', 'hash2');"
                )

    def test_foreign_key_on_delete_cascade(self):
        """Verify that deleting a user deletes user settings and test records automatically (ON DELETE CASCADE)."""
        with self.db.transaction() as conn:
            # Insert User
            cursor = conn.execute(
                "INSERT INTO users (username, display_name, password_hash) "
                "VALUES ('user_test', 'Tester', 'hash_test');"
            )
            user_id = cursor.lastrowid
            
            # Insert User Settings
            conn.execute(
                "INSERT INTO user_settings (user_id, theme, font_family, font_size, language, caret_style) "
                f"VALUES ({user_id}, 'dark', 'Consolas', 14, 'English', 'line');"
            )
            
            # Insert Test Record
            conn.execute(
                "INSERT INTO tests (user_id, completed_at, mode, duration, wpm, raw_wpm, accuracy, characters, correct_characters, incorrect_characters) "
                f"VALUES ({user_id}, '2026-08-26 00:00:00', '15', 15, 60.0, 60.0, 100.0, 75, 75, 0);"
            )

        # Confirm insertion worked
        with self.db.get_connection() as conn:
            user_settings_count = conn.execute("SELECT COUNT(*) FROM user_settings;").fetchone()[0]
            tests_count = conn.execute("SELECT COUNT(*) FROM tests;").fetchone()[0]
            self.assertEqual(user_settings_count, 1)
            self.assertEqual(tests_count, 1)
            
        # Delete user
        with self.db.transaction() as conn:
            conn.execute(f"DELETE FROM users WHERE id = {user_id};")
            
        # Confirm that cascade deletion worked on related child tables
        with self.db.get_connection() as conn:
            user_settings_count = conn.execute("SELECT COUNT(*) FROM user_settings;").fetchone()[0]
            tests_count = conn.execute("SELECT COUNT(*) FROM tests;").fetchone()[0]
            self.assertEqual(user_settings_count, 0)
            self.assertEqual(tests_count, 0)

if __name__ == '__main__':
    unittest.main()
