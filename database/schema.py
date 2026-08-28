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
        consistency REAL,
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
        average_consistency REAL DEFAULT 0.0,
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
        ui_language TEXT DEFAULT 'uz',
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        xp_reward INTEGER NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON DELETE CASCADE,
        UNIQUE(user_id, achievement_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_daily_missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        mission_key TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        progress INTEGER NOT NULL DEFAULT 0,
        target INTEGER NOT NULL,
        xp_reward INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, date, mission_key)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS user_key_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        char_key TEXT NOT NULL,
        attempts INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, char_key)
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
            
            # Apply safe migrations if columns are missing
            for query in [
                "ALTER TABLE tests ADD COLUMN consistency REAL;",
                "ALTER TABLE daily_stats ADD COLUMN average_consistency REAL DEFAULT 0.0;",
                "ALTER TABLE user_settings ADD COLUMN ui_language TEXT DEFAULT 'uz';"
            ]:
                try:
                    conn.execute(query)
                except Exception:
                    pass # Column already exists or table does not match
            
            # Seed default achievements
            achievements_data = [
                ('first_test', 'Birinchi Qadam', 'Birinchi marta yozish mashqini yakunlang', 50),
                ('speed_60', 'Tezlik Ustasi', 'Mashq davomida 60 WPM dan yuqori tezlik ko\'rsating', 100),
                ('speed_100', 'Tezlik Qiroli', 'Mashq davomida 100 WPM dan yuqori tezlik ko\'rsating', 150),
                ('accuracy_100', 'Mukammallik', 'Mashqni 100% aniqlikda yakunlang (kamida 30 soniyalik test)', 100),
                ('streak_3', 'Matonat', 'Kunlik mashq qilish uzluksizligini 3 kunga yetkazing', 100),
                ('streak_7', 'Muntazamlik', 'Kunlik mashq qilish uzluksizligini 7 kunga yetkazing', 150),
                ('level_5', 'Tajribali', 'Dasturda 5-darajaga (Level 5) erishing', 150)
            ]
            for key, title, desc, xp_reward in achievements_data:
                conn.execute(
                    "INSERT OR IGNORE INTO achievements (key, title, description, xp_reward) VALUES (?, ?, ?, ?);",
                    (key, title, desc, xp_reward)
                )
            
            logger.info("Database schema initialized and achievements seeded successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database schema: {e}", exc_info=True)
        raise e
