"""
Personal best database repository for TypeMaster.
"""
from datetime import datetime
from database.repositories.base_repository import BaseRepository

class PersonalBestRepository(BaseRepository):
    """
    Handles database operations for checking and tracking user personal bests.
    """
    def get_personal_best(self, user_id: int, mode: str, duration: int) -> dict:
        """
        Retrieves the current personal best record for a specific user, mode, and duration.
        """
        query = """
            SELECT best_wpm, best_accuracy, achieved_at
            FROM personal_bests
            WHERE user_id = ? AND mode = ? AND duration = ?
        """
        rows = self.execute_query(query, (user_id, mode, duration), use_transaction=True)
        return rows[0] if rows else None

    def check_and_update_pb(self, user_id: int, mode: str, duration: int,
                            wpm: float, accuracy: float) -> bool:
        """
        Checks if the provided WPM/accuracy is a new Personal Best.
        If it exceeds the previous best (or if no previous PB exists),
        saves the new record and returns True. Otherwise, returns False.
        """
        existing = self.get_personal_best(user_id, mode, duration)
        
        if existing is None:
            # First time completing this configuration, automatically a PB
            insert_query = """
                INSERT INTO personal_bests (user_id, mode, duration, best_wpm, best_accuracy, achieved_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            achieved_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            self.execute_write(insert_query, (user_id, mode, duration, wpm, accuracy, achieved_at))
            return True

        current_wpm = existing["best_wpm"]
        current_acc = existing["best_accuracy"]

        # PB is beaten if new WPM is higher, or if WPM is equal but accuracy is better
        is_beaten = (wpm > current_wpm) or (wpm == current_wpm and accuracy > current_acc)

        if is_beaten:
            update_query = """
                UPDATE personal_bests
                SET best_wpm = ?, best_accuracy = ?, achieved_at = ?
                WHERE user_id = ? AND mode = ? AND duration = ?
            """
            achieved_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            self.execute_write(update_query, (wpm, accuracy, achieved_at, user_id, mode, duration))
            return True

        return False

    def get_all_personal_bests(self, user_id: int) -> list:
        """
        Retrieves all personal best records for a user, sorted by achieved date descending.
        """
        query = """
            SELECT id, user_id, mode, duration, best_wpm, best_accuracy, achieved_at
            FROM personal_bests
            WHERE user_id = ?
            ORDER BY achieved_at DESC
        """
        return self.execute_query(query, (user_id,))


