import unittest
from unittest.mock import patch, MagicMock
from services.sound_service import SoundService

class TestSoundToggle(unittest.TestCase):
    def setUp(self):
        # Retrieve sound service singleton instance
        self.sound_service = SoundService()

    def test_guest_toggle_sound(self):
        # Ensure that toggle works correctly in guest state (no active session user)
        with patch('services.auth_service.get_current_user', return_value=None):
            initial_state = self.sound_service._is_sound_enabled()
            new_state = self.sound_service.toggle_sound()
            
            # State should be inverted
            self.assertEqual(new_state, not initial_state)
            self.assertEqual(self.sound_service._is_sound_enabled(), new_state)
            
            # Toggling again should return it to initial state
            restored_state = self.sound_service.toggle_sound()
            self.assertEqual(restored_state, initial_state)
            self.assertEqual(self.sound_service._is_sound_enabled(), initial_state)

    def test_logged_in_toggle_sound(self):
        # Mock active user and SettingsRepository
        mock_user = {"id": 1, "username": "test_user"}
        mock_settings = {"sound_enabled": 1}
        
        with patch('services.auth_service.get_current_user', return_value=mock_user), \
             patch('database.repositories.settings_repository.SettingsRepository.get_settings', return_value=mock_settings), \
             patch('database.repositories.settings_repository.SettingsRepository.update_setting') as mock_update:
            
            # Sound is initially enabled (sound_enabled is 1)
            self.assertTrue(self.sound_service._is_sound_enabled())
            
            # Toggle it off
            new_state = self.sound_service.toggle_sound()
            
            # It should return False and update user's settings row in DB to 0
            self.assertFalse(new_state)
            mock_update.assert_called_with(mock_user["id"], "sound_enabled", 0)
