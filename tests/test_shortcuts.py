"""
Unit tests for TypeMaster Keyboard Shortcuts and TypingTestView.
Verifies keyboard binding mappings, configuration resets, and character highlights.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from ui.typing_test import TypingTestView
from app.application import Application
from database.connection import db
from database.schema import initialize_schema

class TestKeyboardShortcutsAndTestView(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Configure test DB in transaction block
        self.original_db_path = db.database_path
        # We can map connection to in-memory DB or keep default for mock dependencies
        self.controller = MagicMock()
        self.controller.current_theme = "dark"
        self.controller.current_font_family = "Consolas"
        self.controller.current_font_size = 14
        self.controller.root = self.root
        
        # Patch SettingsRepository database querying to avoid sqlite table issues
        self.patcher_settings = patch("database.repositories.settings_repository.SettingsRepository.get_settings")
        self.mock_get_settings = self.patcher_settings.start()
        self.mock_get_settings.return_value = {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "English",
            "sound_enabled": True
        }
        
        self.mock_user = {
            "id": 1,
            "username": "tester",
            "display_name": "Tester",
            "xp": 500,
            "level": 5,
            "current_streak": 2
        }

    def tearDown(self):
        self.patcher_settings.stop()
        # Restore DB path configuration
        db.database_path = self.original_db_path
        self.root.destroy()


    @patch("services.auth_service.get_current_user")
    def test_typing_test_layout_initialization(self, mock_get_user):
        """Verify widgets creation inside TypingTestView."""
        mock_get_user.return_value = self.mock_user
        
        view = TypingTestView(self.root, self.controller)
        view.on_show()
        
        self.assertEqual(view.lang_var.get(), "English")
        self.assertEqual(view.dur_var.get(), "60")
        self.assertIsNotNone(view.text_widget)
        self.assertIsNotNone(view.restart_btn)

        view.on_hide()
        view.destroy()

    @patch("services.auth_service.get_current_user")
    def test_typing_test_on_key_press_and_highlights(self, mock_get_user):
        """Verify keypress changes styling tags inside text widget."""
        mock_get_user.return_value = self.mock_user
        
        view = TypingTestView(self.root, self.controller)
        view.on_show()
        
        view.engine.target_text = "the quick"
        
        # Correct key 't'
        event = MagicMock()
        event.char = "t"
        event.keysym = "t"
        view._on_key_press(event)
        
        self.assertEqual(view.engine.typed_text, "t")
        tags = view.text_widget.tag_names("1.0")
        self.assertIn("correct", tags)
        
        # Incorrect key 'x' (expected 'h')
        event.char = "x"
        event.keysym = "x"
        view._on_key_press(event)
        
        self.assertEqual(view.engine.typed_text, "tx")
        tags_1 = view.text_widget.tag_names("1.1")
        self.assertIn("incorrect", tags_1)
        
        view.on_hide()
        view.destroy()

    @patch("services.auth_service.get_current_user")
    def test_restart_shortcuts(self, mock_get_user):
        """Verify Escape / Tab inputs invoke engine reset and clear labels."""
        mock_get_user.return_value = self.mock_user
        
        view = TypingTestView(self.root, self.controller)
        view.on_show()
        
        # Start test by typing a char
        event = MagicMock()
        event.char = "t"
        event.keysym = "t"
        view._on_key_press(event)
        self.assertTrue(view.engine.is_active)
        self.assertEqual(len(view.engine.typed_text), 1)
        
        # Escape key triggers reset
        event_esc = MagicMock()
        event_esc.char = ""
        event_esc.keysym = "Escape"
        view._on_key_press(event_esc)
        
        self.assertFalse(view.engine.is_active)
        self.assertEqual(view.engine.typed_text, "")
        
        # Start again and reset via Tab
        view._on_key_press(event)
        self.assertTrue(view.engine.is_active)
        
        event_tab = MagicMock()
        event_tab.char = ""
        event_tab.keysym = "Tab"
        view._on_key_press(event_tab)
        
        self.assertFalse(view.engine.is_active)
        self.assertEqual(view.engine.typed_text, "")
        
        view.on_hide()
        view.destroy()

    @patch("services.auth_service.load_session_user")
    def test_global_bindings_registered(self, mock_load):
        """Verify global hotkeys binds are active in root window container."""
        mock_load.return_value = None
        
        app = Application()
        binds = app.root.bind()
        
        # Normalize tk binds lists
        binds_str = [str(b) for b in binds]
        
        # Check Ctrl+H, Ctrl+L, Escape exist
        has_ctrl_h = any("Control" in b and ("h" in b or "H" in b) for b in binds_str)
        has_ctrl_l = any("Control" in b and ("l" in b or "L" in b) for b in binds_str)
        has_escape = any("Escape" in b for b in binds_str)
        
        self.assertTrue(has_ctrl_h, "Ctrl+H binding missing from root window")
        self.assertTrue(has_ctrl_l, "Ctrl+L binding missing from root window")
        self.assertTrue(has_escape, "Escape binding missing from root window")
        
        app.on_close()


if __name__ == '__main__':
    unittest.main()
