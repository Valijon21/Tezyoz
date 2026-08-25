"""
Password security and hashing utilities module for TypeMaster.
Provides iterations, pbkdf2 key derivation, salting, and constant-time verify checks.
"""
import hashlib
import hmac
import os
import sqlite3
import logging
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
        return user_dict
        
    return None
