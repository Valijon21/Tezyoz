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
        
        # Setup paths
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")
        self.click_mp3_path = os.path.join(self.assets_dir, "click.mp3")
        self.click_path = os.path.join(self.assets_dir, "click.wav")
        self.error_path = os.path.join(self.assets_dir, "error.wav")
        self.level_up_path = os.path.join(self.assets_dir, "level_up.wav")
        
        # Check and generate files if missing
        self._ensure_sound_files()
        
        # Initialize Windows MCI player config
        self.mci_open = False
        
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _init_mci(self):
        """Initializes MCI media device mapping to play custom MP3 clicks with low latency."""
        try:
            import ctypes
            # Close existing alias mapping
            ctypes.windll.winmm.mciSendStringW('close click_sound', None, 0, 0)
            res = ctypes.windll.winmm.mciSendStringW(f'open "{self.click_mp3_path}" type mpegvideo alias click_sound', None, 0, 0)
            if res == 0:
                self.mci_open = True
            else:
                logger.warning(f"Failed to open click.mp3 via MCI: status {res}")
        except Exception as err:
            logger.error(f"Error initializing MCI click player sessions: {err}")

    def _ensure_sound_files(self):
        """Builds mechanical sound effects programmatically if they are missing."""
        try:
            if not os.path.exists(self.click_path):
                self._generate_wav_file(self.click_path, frequency=0, duration_ms=60, is_click=True)
            if not os.path.exists(self.error_path):
                self._generate_wav_file(self.error_path, frequency=140, duration_ms=150, is_click=False)
            if not os.path.exists(self.level_up_path):
                self._generate_wav_file(self.level_up_path, frequency=0, duration_ms=600, is_click=False, is_levelup=True)
        except Exception as err:
            logger.error(f"Failed to generate sound assets: {err}")

    def _generate_wav_file(self, filename, frequency, duration_ms, is_click=True, is_levelup=False):
        """Generates raw PCM wave assets and writes standard RIFF headers."""
        import struct
        import math
        import random
        
        sample_rate = 11025
        data = []
        
        if is_click:
            # Mechanical switch click: rapid pitch sweep down and white noise decay
            num_samples = int(sample_rate * (duration_ms / 1000.0))
            for i in range(num_samples):
                t = i / sample_rate
                # Rapid expo decay envelope
                envelope = math.exp(-120 * t)
                # Sweep pitch
                freq = 1800 - 1500 * (i / num_samples)
                val = math.sin(2 * math.pi * freq * t) * envelope
                # High frequency click snap noise
                noise = (random.random() - 0.5) * 0.15 * envelope
                sample_val = max(-1.0, min(1.0, val + noise))
                data.append(int(sample_val * 32767))
        elif is_levelup:
            # Ascending 4-note celebratory chime
            num_samples = int(sample_rate * (duration_ms / 1000.0))
            data = [0] * num_samples
            note_freqs = [523, 659, 784, 1046]  # C5 - E5 - G5 - C6
            for note_idx, freq in enumerate(note_freqs):
                start_sample = int(sample_rate * (note_idx * 0.12))
                note_dur_samples = int(sample_rate * 0.25)
                for i in range(note_dur_samples):
                    curr_sample = start_sample + i
                    if curr_sample >= num_samples:
                        break
                    t = i / sample_rate
                    # Soft chime envelope
                    envelope = math.exp(-9 * t)
                    val = math.sin(2 * math.pi * freq * t) * envelope * 0.25
                    data[curr_sample] = int(data[curr_sample] + val * 32767)
        else:
            # Error buzzer (low frequency tone)
            num_samples = int(sample_rate * (duration_ms / 1000.0))
            for i in range(num_samples):
                t = i / sample_rate
                # Square wave buzz
                val = 0.4 if (math.sin(2 * math.pi * frequency * t) >= 0) else -0.4
                data.append(int(val * 32767))
                
        # Write WAV format
        data_bytes = bytearray()
        for sample in data:
            # Clamp value
            sample = max(-32768, min(32767, sample))
            data_bytes.extend(struct.pack("<h", sample))
            
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + len(data_bytes),
            b"WAVE",
            b"fmt ",
            16,
            1,      # PCM
            1,      # Mono
            sample_rate,
            sample_rate * 2,
            2,      # BlockAlign
            16,     # Bits per sample
            b"data",
            len(data_bytes)
        )
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(header + data_bytes)

    def _worker_loop(self):
        """Worker loop executing beep commands sequentially in daemon thread."""
        # Initialize MCI device alias on this background worker thread
        if winsound and os.path.exists(self.click_mp3_path):
            self._init_mci()

        while True:
            try:
                sound_type = self.sound_queue.get()
                if sound_type is None:
                    # Close MCI session when thread terminates
                    if self.mci_open:
                        try:
                            import ctypes
                            ctypes.windll.winmm.mciSendStringW('close click_sound', None, 0, 0)
                        except Exception:
                            pass
                    break
                
                # Check user settings dynamically before playing sound
                if not self._is_sound_enabled():
                    self.sound_queue.task_done()
                    continue
 
                if winsound:
                    # Resolve filepath based on type
                    file_path = None
                    if sound_type == "click":
                        if self.mci_open:
                            import ctypes
                            ctypes.windll.winmm.mciSendStringW('play click_sound from 0', None, 0, 0)
                        else:
                            file_path = self.click_path
                    elif sound_type == "error":
                        file_path = self.error_path
                    elif sound_type == "level_up":
                        file_path = self.level_up_path
                        
                    if file_path and os.path.exists(file_path):
                        # Play wav file
                        winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    elif not (sound_type == "click" and self.mci_open):
                        # Fallback to beep
                        if sound_type == "click":
                            winsound.Beep(800, 25)
                        elif sound_type == "error":
                            winsound.Beep(250, 100)
                        elif sound_type == "level_up":
                            winsound.Beep(523, 70)
                            winsound.Beep(659, 70)
                            winsound.Beep(784, 70)
                            winsound.Beep(1046, 120)
                
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
