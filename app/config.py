"""
TypeMaster configuration module.
Defines application constants, directory paths, default user settings, and gamification rewards.
"""
from pathlib import Path

# Application Metadata
APP_NAME = "TypeMaster"
APP_VERSION = "1.0.0"

# UI Defaults
DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 600

# File names
DATABASE_FILENAME = "typemaster.db"
LOG_FILENAME = "app.log"

# Path Strategy (Derived relative to project root)
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

DATABASE_PATH = DATA_DIR / DATABASE_FILENAME
LOG_PATH = LOG_DIR / LOG_FILENAME

# Supported Typing Modes (time in seconds)
SUPPORTED_MODES = [15, 30, 60, 120]

# Supported Application/Interface Languages
SUPPORTED_LANGUAGES = ["English", "Russian", "Uzbek"]

# Gamification XP Rules
XP_TEST_COMPLETED = 50
XP_ACCURACY_95 = 20
XP_ACCURACY_98 = 40
XP_PERSONAL_BEST = 100
XP_DAILY_GOAL = 100

# Default User Settings
DEFAULT_THEME = "dark"
DEFAULT_FONT_FAMILY = "Consolas"
DEFAULT_FONT_SIZE = 14
DEFAULT_LANGUAGE = "English"
DEFAULT_SOUND_ENABLED = True
DEFAULT_SHOW_LIVE_WPM = True
DEFAULT_SHOW_ACCURACY = True
DEFAULT_CARET_STYLE = "line"

# Ensure runtime paths exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
