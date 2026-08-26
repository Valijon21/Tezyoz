"""
Unit tests for TypeMaster User-Friendly Error Handling.
Verifies callback runtime exception intercepting and logging.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from app.application import Application

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.patcher_settings = patch("database.repositories.settings_repository.SettingsRepository.get_settings")
        self.mock_get_settings = self.patcher_settings.start()
        self.mock_get_settings.return_value = {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 14,
            "language": "English",
            "sound_enabled": True
        }
        
    def tearDown(self):
        self.patcher_settings.stop()
        self.root.destroy()
        
    @patch("logging.getLogger")
    @patch("tkinter.messagebox.showerror")
    @patch("services.auth_service.load_session_user")
    def test_report_callback_exception(self, mock_load_user, mock_showerror, mock_get_logger):
        """Verify that report_callback_exception logs the exception and shows a popup dialog."""
        mock_load_user.return_value = None
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.object(Application, "_create_views"), patch.object(Application, "_bind_global_shortcuts"):
            app = Application()
            
            dummy_exc = ValueError
            dummy_val = ValueError("Test unexpected runtime error")
            dummy_tb = None
            
            app.report_callback_exception(dummy_exc, dummy_val, dummy_tb)
            
            # Assert logger was accessed to log error
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            self.assertIn("Uncaught runtime exception in event callback", args[0])
            self.assertEqual(kwargs.get("exc_info"), (dummy_exc, dummy_val, dummy_tb))
            
            # Assert messagebox dialog was triggered
            mock_showerror.assert_called_once()
            show_args, _ = mock_showerror.call_args
            self.assertEqual(show_args[0], "Tizim Xatoligi (System Error)")
            self.assertIn("Kutilmagan tizim xatoligi yuz berdi", show_args[1])
            self.assertIn("Test unexpected runtime error", show_args[1])
            
            # Verify root binding was configured
            self.assertEqual(app.root.report_callback_exception, app.report_callback_exception)
