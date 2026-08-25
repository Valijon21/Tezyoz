"""
Database schema definition module for TypeMaster.
Provides table structures and automatic schema initialization.
"""
import logging
from database.connection import db

logger = logging.getLogger("database.schema")

SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_active_date TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        started_at DATETIME,
        completed_at DATETIME NOT NULL,
        mode TEXT NOT NULL,
        duration INTEGER NOT NULL,
        language TEXT,
        difficulty TEXT,
        wpm REAL NOT NULL,
        raw_wpm REAL NOT NULL,
        accuracy REAL NOT NULL,
        characters INTEGER NOT NULL,
        correct_characters INTEGER NOT NULL,
        incorrect_characters INTEGER NOT NULL,
        xp_earned INTEGER DEFAULT 0,
        is_personal_best INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        tests_count INTEGER DEFAULT 0,
        practice_seconds INTEGER DEFAULT 0,
        average_wpm REAL DEFAULT 0.0,
        best_wpm REAL DEFAULT 0.0,
        average_accuracy REAL DEFAULT 0.0,
        best_accuracy REAL DEFAULT 0.0,
        total_characters INTEGER DEFAULT 0,
        total_errors INTEGER DEFAULT 0,
        xp_earned INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS personal_bests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mode TEXT NOT NULL,
        duration INTEGER NOT NULL,
        best_wpm REAL NOT NULL,
        best_accuracy REAL NOT NULL,
        achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, mode, duration)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        theme TEXT NOT NULL,
        font_family TEXT NOT NULL,
        font_size INTEGER NOT NULL,
        language TEXT NOT NULL,
        sound_enabled INTEGER DEFAULT 1,
        show_live_wpm INTEGER DEFAULT 1,
        show_accuracy INTEGER DEFAULT 1,
        caret_style TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """
]

def initialize_schema():
    """Initializes the database schema by executing CREATE TABLE queries within a transaction."""
    logger.info("Initializing database schema...")
    try:
        with db.transaction() as conn:
            for sql in SCHEMA_SQL:
                conn.execute(sql)
            logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database schema: {e}", exc_info=True)
        raise e
