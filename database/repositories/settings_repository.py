"""
User settings database repository for TypeMaster.
"""
import logging
from database.connection import db

logger = logging.getLogger("database.repositories.settings_repository")

class SettingsRepository:
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
        "caret_style"
    }

    def get_settings(self, user_id: int) -> dict:
        """
        Retrieves preference settings for a user.
        Returns a dictionary representation of user settings, or None.
        """
        query = """
            SELECT user_id, theme, font_family, font_size, language,
                   sound_enabled, show_live_wpm, show_accuracy, caret_style
            FROM user_settings
            WHERE user_id = ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

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
            with db.transaction() as conn:
                cursor = conn.execute(query, (value, user_id))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update user setting: {e}", exc_info=True)
            return False
