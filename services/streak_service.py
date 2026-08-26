"""
Streak management and calculation services for TypeMaster.
"""
from datetime import datetime, timedelta
from database.connection import db

class StreakService:
    """
    Handles user practice streak increments, breaks, and persistence.
    """
    def update_streak(self, user_id: int, today_str: str = None) -> dict:
        """
        Calculates and updates user's consecutive day practice streak.
        If today_str is not provided, uses current local date string (YYYY-MM-DD).
        
        Rules:
        - If last active date is today_str: do not increment again.
        - If last active date is yesterday_str: increment streak.
        - Otherwise (including None or multiple days gap): reset current streak to 1.
        - Updates longest streak records if current streak exceeds it.
        """
        if not today_str:
            today_str = datetime.now().strftime("%Y-%m-%d")

        # Calculate yesterday's date string
        try:
            dt = datetime.strptime(today_str, "%Y-%m-%d")
        except ValueError:
            # Fallback for invalid date string inputs in tests
            dt = datetime.now()
            
        yesterday_str = (dt - timedelta(days=1)).strftime("%Y-%m-%d")

        # Fetch current user streak attributes
        select_query = """
            SELECT current_streak, longest_streak, last_active_date
            FROM users
            WHERE id = ?
        """
        
        with db.transaction() as conn:
            cursor = conn.execute(select_query, (user_id,))
            row = cursor.fetchone()
            if not row:
                return {} # User not found
                
            current_streak = row["current_streak"] or 0
            longest_streak = row["longest_streak"] or 0
            last_active = row["last_active_date"]

            # Evaluate updates
            if last_active == today_str:
                # Already active today, streak stays the same
                pass
            elif last_active == yesterday_str:
                # Active yesterday, streak continues!
                current_streak += 1
            else:
                # Streak broke or first time
                current_streak = 1

            # Update longest streak records
            if current_streak > longest_streak:
                longest_streak = current_streak

            # Persist back to sqlite
            update_query = """
                UPDATE users
                SET current_streak = ?, longest_streak = ?, last_active_date = ?
                WHERE id = ?
            """
            conn.execute(update_query, (current_streak, longest_streak, today_str, user_id))

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_active_date": today_str
        }
