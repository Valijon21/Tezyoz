"""
Unit tests for TypeMaster User Session Manager.
Verifies file persistence, memory caching, logout, auto login, and corrupt/missing file handlings.
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
import services.auth_service as auth
from database.schema import initialize_schema
from services.auth_service import (
    register_user,
    login_user,
    get_current_user,
    set_current_user,
    load_session_user,
    logout_user,
    SESSION_FILE_PATH
)

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        # Create tempDB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch auth db path
        self.original_db_path = auth.db.database_path
        auth.db.database_path = self.db_path
        
        # Patch schema db path
        import database.schema as schema
        self.schema_original_db_path = schema.db.database_path
        schema.db.database_path = self.db_path
        initialize_schema()
        
        # Create temp folder for session file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_original_path = auth.SESSION_FILE_PATH
        auth.SESSION_FILE_PATH = Path(self.temp_dir.name) / "session.json"
        
        # Clear memory state
        auth._current_user = None

    def tearDown(self):
        # Restore db/session paths
        auth.db.database_path = self.original_db_path
        import database.schema as schema
        schema.db.database_path = self.schema_original_db_path
        auth.SESSION_FILE_PATH = self.session_original_path
        
        # Clear directory/db files
        self.temp_dir.cleanup()
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass
            
        auth._current_user = None

    def test_set_current_user_persists_session(self):
        """Verify set_current_user caches in memory and writes user ID to session.json."""
        user_id = register_user("test_user", "Tester", "password123")
        user = {"id": user_id, "username": "test_user"}
        
        set_current_user(user)
        self.assertEqual(get_current_user(), user)
        self.assertTrue(auth.SESSION_FILE_PATH.exists())
        
        with open(auth.SESSION_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("last_active_user_id"), user_id)

    def test_load_session_user_auto_logins(self):
        """Verify load_session_user loads user from session file and saves to memory."""
        user_id = register_user("test_user", "Tester", "password123")
        
        # Set file manually to mock previous session
        with open(auth.SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"last_active_user_id": user_id}, f)
            
        loaded_user = load_session_user()
        self.assertIsNotNone(loaded_user)
        self.assertEqual(loaded_user["username"], "test_user")
        self.assertEqual(get_current_user(), loaded_user)

    def test_clear_session_on_logout(self):
        """Verify logout clears memory and unlinks session file."""
        user_id = register_user("test_user", "Tester", "password123")
        user = {"id": user_id, "username": "test_user"}
        
        set_current_user(user)
        self.assertTrue(auth.SESSION_FILE_PATH.exists())
        
        logout_user()
        self.assertIsNone(get_current_user())
        self.assertFalse(auth.SESSION_FILE_PATH.exists())

    def test_load_session_corrupt_file(self):
        """Verify corrupted session file returns None and drops it safely."""
        with open(auth.SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("corrupted json content{")
            
        loaded = load_session_user()
        self.assertIsNone(loaded)
        self.assertFalse(auth.SESSION_FILE_PATH.exists())

    def test_load_session_user_not_in_db(self):
        """Verify missing user in database deletes the orphan session file."""
        with open(auth.SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump({"last_active_user_id": 99999}, f) # Non-existent user ID
            
        loaded = load_session_user()
        self.assertIsNone(loaded)
        self.assertFalse(auth.SESSION_FILE_PATH.exists())

if __name__ == '__main__':
    unittest.main()
