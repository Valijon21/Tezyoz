"""
Password security and hashing utilities module for TypeMaster.
Provides iterations, pbkdf2 key derivation, salting, and constant-time verify checks.
"""
import hashlib
import hmac
import os
import sqlite3
import logging
import json
from database.connection import db
from app.config import (
    DEFAULT_THEME,
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    DEFAULT_LANGUAGE,
    DEFAULT_SOUND_ENABLED,
    DEFAULT_SHOW_LIVE_WPM,
    DEFAULT_SHOW_ACCURACY,
    DEFAULT_CARET_STYLE
)

logger = logging.getLogger("services.auth_service")

# NIST recommended minimum iterations for PBKDF2 with SHA-256
PBKDF2_ITERATIONS = 100000

# Global user session state
_current_user = None
SESSION_FILE_PATH = db.database_path.parent / "session.json"

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256.
    Generates a secure random 16-byte salt.
    Returns format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )
    salt_hex = salt.hex()
    hash_hex = derived_key.hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_hex}${hash_hex}"

def verify_password(password: str, hashed_value: str) -> bool:
    """
    Verifies a password against its PBKDF2-HMAC-SHA256 hash.
    Performs parsing validation and constant-time string comparison.
    """
    if not hashed_value or not isinstance(hashed_value, str):
        return False
        
    parts = hashed_value.split('$')
    if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
        logger.warning("Attempted to verify password with unrecognized hash format.")
        return False
        
    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
    except ValueError as err:
        logger.error(f"Failed to parse database password hash components: {err}")
        return False
        
    # Reconstruct the candidate hash using the same iterations and salt
    candidate_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    
    # Timing-attacker resistant equality check
    return hmac.compare_digest(candidate_hash, expected_hash)

def register_user(username: str, display_name: str, password: str) -> int:
    """
    Registers a new user inside the database in a transaction context.
    Generates default preference options inside local user_settings table automatically.
    Raises ValueError if username is empty, too short, or already registered.
    """
    username = username.strip()
    display_name = display_name.strip() or username
    password = password.strip()
    
    if not username:
        raise ValueError("Foydalanuvchi nomi kiritilishi shart!")
    if len(password) < 6:
        raise ValueError("Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
        
    # Salt and hash password candidate
    password_hash = hash_password(password)
    
    try:
        with db.transaction() as conn:
            # Duplicate Check
            cursor = conn.execute("SELECT 1 FROM users WHERE username = ?;", (username,))
            if cursor.fetchone():
                raise ValueError("Bu foydalanuvchi nomi allaqachon ro'yxatdan o'tkazilgan!")
                
            # Insert User record
            user_cursor = conn.execute(
                "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?);",
                (username, display_name, password_hash)
            )
            user_id = user_cursor.lastrowid
            
            # Set Default settings constraints in transaction block
            conn.execute(
                "INSERT INTO user_settings (user_id, theme, font_family, font_size, language, sound_enabled, show_live_wpm, show_accuracy, caret_style) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (
                    user_id,
                    DEFAULT_THEME,
                    DEFAULT_FONT_FAMILY,
                    DEFAULT_FONT_SIZE,
                    DEFAULT_LANGUAGE,
                    1 if DEFAULT_SOUND_ENABLED else 0,
                    1 if DEFAULT_SHOW_LIVE_WPM else 0,
                    1 if DEFAULT_SHOW_ACCURACY else 0,
                    DEFAULT_CARET_STYLE
                )
            )
            
            # Auto save last active user ID to session persistence file:
            _save_session(user_id)
            return user_id
    except sqlite3.IntegrityError as err:
        logger.error(f"Database integrity constraints violation during user registry: {err}")
        raise ValueError(f"Tizim xatoligi yuz berdi: {err}")

def login_user(username: str, password: str) -> dict:
    """
    Logs in a user.
    Queries users, verifies password, and returns dictionary representing user details.
    Returns None if username or password does not match.
    """
    username = username.strip()
    password = password.strip()
    
    if not username or not password:
        return None
        
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, display_name, password_hash, xp, level, current_streak, longest_streak FROM users WHERE username = ?;",
            (username,)
        )
        row = cursor.fetchone()
        
    if not row:
        return None
        
    user_dict = dict(row)
    if verify_password(password, user_dict["password_hash"]):
        # Remove password hash for safety reasons when passing dict
        del user_dict["password_hash"]
        set_current_user(user_dict)
        return user_dict
        
    return None

def get_current_user() -> dict:
    """Returns the currently active user session from memory, or None."""
    global _current_user
    return _current_user

def set_current_user(user: dict):
    """Sets the active user session in memory and persists the user ID."""
    global _current_user
    _current_user = user
    if user:
        _save_session(user["id"])
    else:
        _clear_session()

def _save_session(user_id: int):
    """Saves user ID to session.json file."""
    try:
        data = {"last_active_user_id": user_id}
        with open(SESSION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as err:
        logger.error(f"Failed to save session file: {err}")

def _clear_session():
    """Removes user ID from session.json file."""
    try:
        if SESSION_FILE_PATH.exists():
            SESSION_FILE_PATH.unlink()
    except Exception as err:
        logger.error(f"Failed to delete session file: {err}")

def load_session_user() -> dict:
    """Reads session.json and automatically retrieves the user details from DB."""
    global _current_user
    if not SESSION_FILE_PATH.exists():
        return None
        
    try:
        with open(SESSION_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        user_id = data.get("last_active_user_id")
    except Exception as err:
        logger.error(f"Failed to read session file: {err}")
        _clear_session()
        return None
        
    if not user_id:
        return None
        
    # Query database to retrieve user details
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, display_name, xp, level, current_streak, longest_streak FROM users WHERE id = ?;",
            (user_id,)
        )
        row = cursor.fetchone()
        
    if not row:
        logger.warning(f"Session user ID {user_id} not found in database. Clearing session.")
        _clear_session()
        return None
        
    _current_user = dict(row)
    return _current_user

def logout_user():
    """Logs out the active user session, clearing memory and session file."""
    set_current_user(None)
