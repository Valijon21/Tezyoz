"""
Background sound effects service for TypeMaster.
Plays click, error, and level-up sounds using winsound.Beep in a separate daemon thread
to avoid blocking the main Tkinter UI thread.
"""
import os
import queue
import threading
import logging

logger = logging.getLogger("services.sound_service")

# Try to import winsound (standard on Windows)
try:
    import winsound
except ImportError:
    winsound = None
    logger.warning("winsound module not found. Sound effects will not be played.")

class SoundService:
    """
    Asynchronous Queue-based Sound Service.
    Spawns a background daemon thread to process sound requests.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SoundService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.sound_queue = queue.Queue()
        self.guest_sound_enabled = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _worker_loop(self):
        """Worker loop executing beep commands sequentially in daemon thread."""
        while True:
            try:
                sound_type = self.sound_queue.get()
                if sound_type is None:
                    break
                
                # Check user settings dynamically before playing sound
                if not self._is_sound_enabled():
                    self.sound_queue.task_done()
                    continue

                if winsound:
                    if sound_type == "click":
                        winsound.Beep(800, 25)
                    elif sound_type == "error":
                        winsound.Beep(250, 100)
                    elif sound_type == "level_up":
                        # Arpeggio sequence for level up
                        winsound.Beep(523, 70)  # C5
                        winsound.Beep(659, 70)  # E5
                        winsound.Beep(784, 70)  # G5
                        winsound.Beep(1046, 120) # C6
                
                self.sound_queue.task_done()
            except Exception as err:
                logger.error(f"Error playing sound in background thread: {err}")

    def _is_sound_enabled(self) -> bool:
        """Helper to resolve settings and check if sounds are turned on."""
        try:
            from services.auth_service import get_current_user
            user = get_current_user()
            if not user:
                return self.guest_sound_enabled
                
            from database.repositories.settings_repository import SettingsRepository
            settings = SettingsRepository().get_settings(user["id"])
            if settings:
                # database stores 1 for enabled, 0 for disabled
                return settings.get("sound_enabled", 1) == 1
        except Exception as err:
            logger.error(f"Error checking sound settings: {err}")
        return self.guest_sound_enabled

    def toggle_sound(self) -> bool:
        """Toggles the sound enabled state. Returns the new sound enabled state."""
        try:
            from services.auth_service import get_current_user
            user = get_current_user()
            
            # Resolve current status
            current_state = self._is_sound_enabled()
            new_state = not current_state
            
            if user:
                from database.repositories.settings_repository import SettingsRepository
                SettingsRepository().update_setting(user["id"], "sound_enabled", 1 if new_state else 0)
            else:
                self.guest_sound_enabled = new_state
                
            return new_state
        except Exception as err:
            logger.error(f"Error toggling sound setting: {err}")
            self.guest_sound_enabled = not self.guest_sound_enabled
            return self.guest_sound_enabled

    def play_click(self):
        """Queue a standard keystroke click sound."""
        self.sound_queue.put("click")

    def play_error(self):
        """Queue a keystroke mismatch error sound."""
        self.sound_queue.put("error")

    def play_level_up(self):
        """Queue a progressive level up arpeggio celebratory sound."""
        self.sound_queue.put("level_up")

# Global singleton client instance
sound_player = SoundService()
