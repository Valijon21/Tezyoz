"""
Unit tests for TypeMaster Logout actions.
Verifies session clearance, database state checks and application redirection paths.
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
    logout_user,
    SESSION_FILE_PATH
)

class TestLogoutFlow(unittest.TestCase):
    def setUp(self):
        # Create tempDB
        self.db_fd, self.db_path_str = tempfile.mkstemp()
        self.db_path = Path(self.db_path_str)
        
        # Patch paths
        self.original_db_path = auth.db.database_path
        auth.db.database_path = self.db_path
        
        import database.schema as schema
        self.schema_original_db_path = schema.db.database_path
        schema.db.database_path = self.db_path
        initialize_schema()
        
        # Temp folder for session
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_original_path = auth.SESSION_FILE_PATH
        auth.SESSION_FILE_PATH = Path(self.temp_dir.name) / "session.json"
        
        auth._current_user = None

    def tearDown(self):
        auth.db.database_path = self.original_db_path
        import database.schema as schema
        schema.db.database_path = self.schema_original_db_path
        auth.SESSION_FILE_PATH = self.session_original_path
        
        self.temp_dir.cleanup()
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path_str)
        except OSError:
            pass
            
        auth._current_user = None

    def test_logout_clears_memory_and_persits(self):
        """Verify that logging out clears both session memory and session file."""
        register_user("logout_tester", "Logout Test", "mypassword123")
        
        # Login to start session
        user_dict = login_user("logout_tester", "mypassword123")
        self.assertIsNotNone(user_dict)
        self.assertEqual(get_current_user(), user_dict)
        self.assertTrue(auth.SESSION_FILE_PATH.exists())
        
        # Logout
        logout_user()
        self.assertIsNone(get_current_user())
        self.assertFalse(auth.SESSION_FILE_PATH.exists())

    def test_logout_view_redirection_flow(self):
        """Verify that view logout handler triggers logout_user and transition requests."""
        register_user("runner", "Runner", "runnerpass")
        login_user("runner", "runnerpass")
        
        # Stub the controller to check navigation redirect
        class MockController:
            def __init__(self):
                self.navigated_view = None
            def show_view(self, name):
                self.navigated_view = name
                
        # Mock Parent
        import tkinter as tk
        root = tk.Tk()
        mock_controller = MockController()
        
        try:
            from app.application import HomePlaceholderView
            home_view = HomePlaceholderView(root, mock_controller)
            
            # Trigger logout action
            home_view.handle_logout()
            
            # AssertIONS
            self.assertIsNone(get_current_user())
            self.assertFalse(auth.SESSION_FILE_PATH.exists())
            self.assertEqual(mock_controller.navigated_view, "login")
        finally:
            root.destroy()

if __name__ == '__main__':
    unittest.main()
