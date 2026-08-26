"""
Key error statistics database repository for TypeMaster.
Provides interfaces to increment attempt/error metrics and query weak keys.
"""
from database.connection import db

class KeyStatsRepository:
    """
    Handles database operations for character-level key attempts and error rates.
    """
    def record_key_stats(self, user_id: int, char_attempts: dict, char_errors: dict):
        """
        Increment attempts and errors count for a batch of key characters using ON CONFLICT logic.
        """
        all_keys = set(char_attempts.keys()) | set(char_errors.keys())
        records = []
        for k in all_keys:
            # We enforce saving lowercase representations of character keys
            cleaned_key = k.lower()
            if len(cleaned_key) != 1:
                continue # ignore anything that is not a single character
            
            att = char_attempts.get(k, 0)
            err = char_errors.get(k, 0)
            if att > 0 or err > 0:
                records.append((user_id, cleaned_key, att, err))
                
        if not records:
            return

        query = """
            INSERT INTO user_key_stats (user_id, char_key, attempts, errors)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, char_key) DO UPDATE SET
                attempts = attempts + excluded.attempts,
                errors = errors + excluded.errors
        """
        with db.transaction() as conn:
            conn.executemany(query, records)

    def get_top_error_keys(self, user_id: int, limit: int = 10) -> list[dict]:
        """
        Retrieves top character keys sorted by total error count descending.
        """
        query = """
            SELECT char_key, attempts, errors
            FROM user_key_stats
            WHERE user_id = ? AND errors > 0
            ORDER BY errors DESC, attempts DESC
            LIMIT ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(query, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_weak_keys(self, user_id: int, min_attempts: int = 5, limit: int = 5) -> list[dict]:
        """
        Retrieves character keys with the highest error rate percentage.
        Calculated as (errors * 100.0) / attempts.
        """
        query = """
            SELECT char_key, attempts, errors,
                   (CAST(errors AS REAL) / attempts) * 100.0 AS error_rate
            FROM user_key_stats
            WHERE user_id = ? AND attempts >= ? AND errors > 0
            ORDER BY error_rate DESC, attempts DESC
            LIMIT ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(query, (user_id, min_attempts, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_key_stats(self, user_id: int) -> dict[str, dict]:
        """
        Retrieves all key statistics for a user, returning a dictionary mapping character keys to stats.
        """
        query = """
            SELECT char_key, attempts, errors,
                   (CAST(errors AS REAL) / attempts) * 100.0 AS error_rate
            FROM user_key_stats
            WHERE user_id = ?
        """
        with db.get_connection() as conn:
            cursor = conn.execute(query, (user_id,))
            return {row["char_key"]: dict(row) for row in cursor.fetchall()}
