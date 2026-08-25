"""
Unit tests for TypeMaster User Login, Registration and settings integration services.
Verifies database transaction registry, duplicates checks, transaction rollbacks and login status.
"""
import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
from database.connection import DatabaseConnection
from services.auth_service import register_user, login_user

class TestLoginService(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to hold the test SQLite DB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch the connection.py database target
        import services.auth_service as auth
        self.auth_db = auth.db
        self.original_db_path = self.auth_db.database_path
        self.auth_db.database_path = self.db_path
        
        # Initialise Schema on this test DB
        from database.schema import initialize_schema
        import database.schema as schema
        self.schema_original_db_path = schema.db.database_path
        schema.db.database_path = self.db_path
        initialize_schema()

    def tearDown(self):
        # Restore db paths
        import services.auth_service as auth
        auth.db.database_path = self.original_db_path
        import database.schema as schema
        schema.db.database_path = self.schema_original_db_path
        
        # Remove temporary DB
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass

    def test_register_creates_user_and_settings(self):
        """Verify successful user registration creates both user and default settings record."""
        user_id = register_user("user1", "User One", "securepass123")
        self.assertGreater(user_id, 0)
        
        # Inspect users
        with self.auth_db.get_connection() as conn:
            user_row = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
            self.assertIsNotNone(user_row)
            self.assertEqual(user_row["username"], "user1")
            self.assertEqual(user_row["display_name"], "User One")
            
            # Inspect default settings creation
            settings_row = conn.execute("SELECT * FROM user_settings WHERE user_id = ?;", (user_id,)).fetchone()
            self.assertIsNotNone(settings_row)
            self.assertEqual(settings_row["theme"], "dark")

    def test_register_username_taken(self):
        """Verify registering a duplicate username raises ValueError."""
        register_user("user1", "User One", "securepass123")
        
        with self.assertRaises(ValueError) as ctx:
            register_user("user1", "User Two", "securepass999")
            
        self.assertEqual(str(ctx.exception), "Bu foydalanuvchi nomi allaqachon ro'yxatdan o'tkazilgan!")

    def test_register_rolls_back_on_settings_failure(self):
        """Verify that a failure during user_settings insertion rolls back the user record completely."""
        import services.auth_service as auth
        original_theme = auth.DEFAULT_THEME
        
        try:
            auth.DEFAULT_THEME = None # Will violate NOT NULL constraint on user_settings.theme
            with self.assertRaises(Exception):
                register_user("corrupt_user", "Corrupt", "securepass123")
                
            # Verify "corrupt_user" was rolled back and does not exist in users table
            with self.auth_db.get_connection() as conn:
                user_row = conn.execute("SELECT * FROM users WHERE username = 'corrupt_user';").fetchone()
                self.assertIsNone(user_row)
        finally:
            auth.DEFAULT_THEME = original_theme

    def test_login_success(self):
        """Verify logging in with correct credentials returns the user details dict."""
        register_user("login_user", "Login Tester", "correct_password")
        
        user_dict = login_user("login_user", "correct_password")
        self.assertIsNotNone(user_dict)
        self.assertEqual(user_dict["username"], "login_user")
        self.assertEqual(user_dict["display_name"], "Login Tester")
        self.assertNotIn("password_hash", user_dict) # Safety constraint check

    def test_login_fail_invalid_username(self):
        """Verify login returns None for non-existent usernames."""
        user_dict = login_user("nonexistent_user", "password123")
        self.assertIsNone(user_dict)

    def test_login_fail_wrong_password(self):
        """Verify login returns None for incorrect password checks."""
        register_user("login_user", "Login Tester", "correct_password")
        user_dict = login_user("login_user", "wrong_password")
        self.assertIsNone(user_dict)

if __name__ == '__main__':
    unittest.main()
