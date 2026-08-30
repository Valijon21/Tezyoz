"""
User settings database repository for TypeMaster.
"""
import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger("database.repositories.settings_repository")

class SettingsRepository(BaseRepository):
    """
    Handles user preferences retrieval and updates, including theme, font, and interface settings.
    """
    VALID_KEYS = {
        "theme",
        "font_family",
        "font_size",
        "language",
        "sound_enabled",
        "show_live_wpm",
        "show_accuracy",
        "caret_style",
        "ui_language",
        "show_keyboard_helper",
        "custom_duration"
    }

    def get_settings(self, user_id: int) -> dict:
        """
        Retrieves preference settings for a user.
        Returns a dictionary representation of user settings, or None.
        """
        query = """
            SELECT user_id, theme, font_family, font_size, language,
                   sound_enabled, show_live_wpm, show_accuracy, caret_style, ui_language,
                   show_keyboard_helper, custom_duration
            FROM user_settings
            WHERE user_id = ?
        """
        rows = self.execute_query(query, (user_id,))
        return rows[0] if rows else None

    def update_setting(self, user_id: int, key: str, value: any) -> bool:
        """
        Updates a specific user setting field securely.
        Returns True if successful, False otherwise.
        """
        if key not in self.VALID_KEYS:
            logger.warning(f"Rejected attempt to update invalid setting key: {key}")
            return False

        # Safe parameter substitution for whitelisted column key
        query = f"UPDATE user_settings SET {key} = ? WHERE user_id = ?"
        
        try:
            self.execute_write(query, (value, user_id))
            return True
        except Exception as e:
            logger.error(f"Failed to update user setting: {e}", exc_info=True)
            return False

