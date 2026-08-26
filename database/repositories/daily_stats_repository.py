"""
Daily statistics database repository for TypeMaster.
"""
from datetime import datetime, timedelta
from database.connection import db

class DailyStatsRepository:
    """
    Handles database operations for aggregating, upserting, and retrieving daily user stats.
    """
    def _calculate_growth(self, current: float, previous: float) -> float:
        """
        Calculates the growth percentage between two values.
        If the previous value is 0.0, handling is explicit to avoid division by zero:
        - If current is also 0.0, growth is 0.0.
        - If current > 0.0, growth is 100.0.
        """
        if previous == 0.0:
            return 100.0 if current > 0.0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    def get_daily_stats(self, user_id: int, date_str: str) -> dict:
        """
        Retrieves aggregated stats for the specified user and date.
        If no record exists, returns a dictionary of default zero metrics.
        """
        try:
            curr_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            curr_dt = datetime.now()
            date_str = curr_dt.strftime("%Y-%m-%d")
        yesterday_str = (curr_dt - timedelta(days=1)).strftime("%Y-%m-%d")

        query = """
            SELECT tests_count, practice_seconds, average_wpm, best_wpm,
                   average_accuracy, best_accuracy, total_characters, total_errors, xp_earned,
                   average_consistency
            FROM daily_stats
            WHERE user_id = ? AND date = ?
        """
        yesterday_query = "SELECT average_wpm FROM daily_stats WHERE user_id = ? AND date = ?"

        with db.transaction() as conn:
            cursor = conn.execute(query, (user_id, date_str))
            row = cursor.fetchone()
            
            cursor_y = conn.execute(yesterday_query, (user_id, yesterday_str))
            row_y = cursor_y.fetchone()
            yesterday_wpm = row_y["average_wpm"] if (row_y and row_y["average_wpm"] is not None) else 0.0

        if row:
            stats = dict(row)
            stats["growth"] = self._calculate_growth(stats["average_wpm"], yesterday_wpm)
            return stats

        # Fallback default statistics when no records exist
        return {
            "tests_count": 0,
            "practice_seconds": 0,
            "average_wpm": 0.0,
            "best_wpm": 0.0,
            "average_accuracy": 0.0,
            "best_accuracy": 0.0,
            "total_characters": 0,
            "total_errors": 0,
            "xp_earned": 0,
            "average_consistency": 0.0,
            "growth": self._calculate_growth(0.0, yesterday_wpm)
        }

    def update_daily_stats(self, user_id: int, date_str: str) -> dict:
        """
        Aggregates completed test outcomes from tests table for a user on
        a specific date (YYYY-MM-DD), and upserts results into daily_stats.
        Returns the updated stats dictionary.
        """
        # Query test stats completed today matching user_id
        aggregate_query = """
            SELECT 
                COUNT(*) as tests_count,
                SUM(duration) as total_duration,
                AVG(wpm) as average_wpm,
                MAX(wpm) as best_wpm,
                AVG(accuracy) as average_accuracy,
                MAX(accuracy) as best_accuracy,
                SUM(characters) as total_characters,
                SUM(incorrect_characters) as total_errors,
                SUM(xp_earned) as total_xp,
                AVG(consistency) as average_consistency
            FROM tests
            WHERE user_id = ? AND date(completed_at) = ?
        """

        upsert_query = """
            INSERT INTO daily_stats (
                user_id, date, tests_count, practice_seconds, average_wpm, best_wpm,
                average_accuracy, best_accuracy, total_characters, total_errors, xp_earned,
                average_consistency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                tests_count = excluded.tests_count,
                practice_seconds = excluded.practice_seconds,
                average_wpm = excluded.average_wpm,
                best_wpm = excluded.best_wpm,
                average_accuracy = excluded.average_accuracy,
                best_accuracy = excluded.best_accuracy,
                total_characters = excluded.total_characters,
                total_errors = excluded.total_errors,
                xp_earned = excluded.xp_earned,
                average_consistency = excluded.average_consistency
        """

        try:
            curr_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            curr_dt = datetime.now()
            date_str = curr_dt.strftime("%Y-%m-%d")
        yesterday_str = (curr_dt - timedelta(days=1)).strftime("%Y-%m-%d")

        with db.transaction() as conn:
            cursor = conn.execute(aggregate_query, (user_id, date_str))
            row = cursor.fetchone()
            
            # If no tests exist for this user on the date, we default values
            tests_count = row["tests_count"] or 0
            if tests_count == 0:
                # No tests done, stats are zeros
                stats = {
                    "tests_count": 0,
                    "practice_seconds": 0,
                    "average_wpm": 0.0,
                    "best_wpm": 0.0,
                    "average_accuracy": 0.0,
                    "best_accuracy": 0.0,
                    "total_characters": 0,
                    "total_errors": 0,
                    "xp_earned": 0,
                    "average_consistency": 0.0
                }
            else:
                stats = {
                    "tests_count": tests_count,
                    "practice_seconds": row["total_duration"] or 0,
                    "average_wpm": round(row["average_wpm"] or 0.0, 2),
                    "best_wpm": round(row["best_wpm"] or 0.0, 2),
                    "average_accuracy": round(row["average_accuracy"] or 0.0, 2),
                    "best_accuracy": round(row["best_accuracy"] or 0.0, 2),
                    "total_characters": row["total_characters"] or 0,
                    "total_errors": row["total_errors"] or 0,
                    "xp_earned": row["total_xp"] or 0,
                    "average_consistency": round(row["average_consistency"] or 0.0, 2)
                }

            if tests_count > 0:
                conn.execute(upsert_query, (
                    user_id, date_str,
                    stats["tests_count"], stats["practice_seconds"],
                    stats["average_wpm"], stats["best_wpm"],
                    stats["average_accuracy"], stats["best_accuracy"],
                    stats["total_characters"], stats["total_errors"], stats["xp_earned"],
                    stats["average_consistency"]
                ))
            
            # Query yesterday's average WPM to calculate growth
            cursor_y = conn.execute("SELECT average_wpm FROM daily_stats WHERE user_id = ? AND date = ?", (user_id, yesterday_str))
            row_y = cursor_y.fetchone()
            yesterday_wpm = row_y["average_wpm"] if (row_y and row_y["average_wpm"] is not None) else 0.0

        stats["growth"] = self._calculate_growth(stats["average_wpm"], yesterday_wpm)
        return stats

    def get_weekly_stats(self, user_id: int, end_date_str: str) -> dict:
        """
        Calculates and returns aggregated week-level practice stats (WPM, accuracy averages, practice durations)
        along with a list of 7 consecutive daily statistics ending at end_date_str.
        """
        # Parse end date and calculate start date (6 days prior)
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            end_dt = datetime.now()
            end_date_str = end_dt.strftime("%Y-%m-%d")

        start_dt = end_dt - timedelta(days=6)
        start_date_str = start_dt.strftime("%Y-%m-%d")

        # Query summary metrics
        summary_query = """
            SELECT 
                SUM(tests_count) as total_tests,
                SUM(practice_seconds) as total_practice_seconds,
                AVG(average_wpm) as average_wpm,
                MAX(best_wpm) as best_wpm,
                AVG(average_accuracy) as average_accuracy,
                MAX(best_accuracy) as best_accuracy,
                SUM(total_characters) as total_characters,
                SUM(total_errors) as total_errors,
                SUM(xp_earned) as total_xp,
                AVG(average_consistency) as average_consistency
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
        """

        # Query all existing daily stats in range
        days_query = """
            SELECT date, tests_count, practice_seconds, average_wpm, best_wpm,
                   average_accuracy, best_accuracy, total_characters, total_errors, xp_earned,
                   average_consistency
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """

        # Calculate previous week's boundaries
        prev_end_dt = start_dt - timedelta(days=1)
        prev_start_dt = start_dt - timedelta(days=7)
        prev_end_str = prev_end_dt.strftime("%Y-%m-%d")
        prev_start_str = prev_start_dt.strftime("%Y-%m-%d")

        with db.transaction() as conn:
            cursor = conn.execute(summary_query, (user_id, start_date_str, end_date_str))
            row = cursor.fetchone()
            
            cursor_days = conn.execute(days_query, (user_id, start_date_str, end_date_str))
            db_days = {r["date"]: dict(r) for r in cursor_days.fetchall()}

            # Query average WPM for previous week to calculate growth
            cursor_prev = conn.execute(
                "SELECT AVG(average_wpm) as average_wpm FROM daily_stats WHERE user_id = ? AND date BETWEEN ? AND ?",
                (user_id, prev_start_str, prev_end_str)
            )
            row_prev = cursor_prev.fetchone()
            prev_average_wpm = row_prev["average_wpm"] if (row_prev and row_prev["average_wpm"] is not None) else 0.0

        # Build summary dict
        if row and row["total_tests"] and row["total_tests"] > 0:
            summary = {
                "tests_count": row["total_tests"],
                "practice_seconds": row["total_practice_seconds"],
                "average_wpm": round(row["average_wpm"] or 0.0, 2),
                "best_wpm": round(row["best_wpm"] or 0.0, 2),
                "average_accuracy": round(row["average_accuracy"] or 0.0, 2),
                "best_accuracy": round(row["best_accuracy"] or 0.0, 2),
                "total_characters": row["total_characters"],
                "total_errors": row["total_errors"],
                "xp_earned": row["total_xp"],
                "average_consistency": round(row["average_consistency"] or 0.0, 2)
            }
        else:
            summary = {
                "tests_count": 0,
                "practice_seconds": 0,
                "average_wpm": 0.0,
                "best_wpm": 0.0,
                "average_accuracy": 0.0,
                "best_accuracy": 0.0,
                "total_characters": 0,
                "total_errors": 0,
                "xp_earned": 0,
                "average_consistency": 0.0
            }
        
        summary["growth"] = self._calculate_growth(summary["average_wpm"], prev_average_wpm)

        # Build daily series sequence
        days_list = []
        for i in range(7):
            current_dt = start_dt + timedelta(days=i)
            curr_str = current_dt.strftime("%Y-%m-%d")
            
            if curr_str in db_days:
                days_list.append(db_days[curr_str])
            else:
                days_list.append({
                    "date": curr_str,
                    "tests_count": 0,
                    "practice_seconds": 0,
                    "average_wpm": 0.0,
                    "best_wpm": 0.0,
                    "average_accuracy": 0.0,
                    "best_accuracy": 0.0,
                    "total_characters": 0,
                    "total_errors": 0,
                    "xp_earned": 0,
                    "average_consistency": 0.0
                })

        return {
            "summary": summary,
            "days": days_list
        }

    def get_monthly_stats(self, user_id: int, end_date_str: str) -> dict:
        """
        Calculates and returns aggregated 30-day practice stats (WPM, accuracy averages, practice durations)
        along with a list of 30 consecutive daily statistics ending at end_date_str.
        """
        # Parse end date and calculate start date (29 days prior)
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            end_dt = datetime.now()
            end_date_str = end_dt.strftime("%Y-%m-%d")

        start_dt = end_dt - timedelta(days=29)
        start_date_str = start_dt.strftime("%Y-%m-%d")

        # Query summary metrics
        summary_query = """
            SELECT 
                SUM(tests_count) as total_tests,
                SUM(practice_seconds) as total_practice_seconds,
                AVG(average_wpm) as average_wpm,
                MAX(best_wpm) as best_wpm,
                AVG(average_accuracy) as average_accuracy,
                MAX(best_accuracy) as best_accuracy,
                SUM(total_characters) as total_characters,
                SUM(total_errors) as total_errors,
                SUM(xp_earned) as total_xp,
                AVG(average_consistency) as average_consistency
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
        """

        # Query all existing daily stats in range
        days_query = """
            SELECT date, tests_count, practice_seconds, average_wpm, best_wpm,
                   average_accuracy, best_accuracy, total_characters, total_errors, xp_earned,
                   average_consistency
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """

        # Calculate previous month's boundaries
        prev_end_dt = start_dt - timedelta(days=1)
        prev_start_dt = start_dt - timedelta(days=30)
        prev_end_str = prev_end_dt.strftime("%Y-%m-%d")
        prev_start_str = prev_start_dt.strftime("%Y-%m-%d")

        with db.transaction() as conn:
            cursor = conn.execute(summary_query, (user_id, start_date_str, end_date_str))
            row = cursor.fetchone()
            
            cursor_days = conn.execute(days_query, (user_id, start_date_str, end_date_str))
            db_days = {r["date"]: dict(r) for r in cursor_days.fetchall()}

            # Query average WPM for previous month to calculate growth
            cursor_prev = conn.execute(
                "SELECT AVG(average_wpm) as average_wpm FROM daily_stats WHERE user_id = ? AND date BETWEEN ? AND ?",
                (user_id, prev_start_str, prev_end_str)
            )
            row_prev = cursor_prev.fetchone()
            prev_average_wpm = row_prev["average_wpm"] if (row_prev and row_prev["average_wpm"] is not None) else 0.0

        # Build summary dict
        if row and row["total_tests"] and row["total_tests"] > 0:
            summary = {
                "tests_count": row["total_tests"],
                "practice_seconds": row["total_practice_seconds"],
                "average_wpm": round(row["average_wpm"] or 0.0, 2),
                "best_wpm": round(row["best_wpm"] or 0.0, 2),
                "average_accuracy": round(row["average_accuracy"] or 0.0, 2),
                "best_accuracy": round(row["best_accuracy"] or 0.0, 2),
                "total_characters": row["total_characters"],
                "total_errors": row["total_errors"],
                "xp_earned": row["total_xp"],
                "average_consistency": round(row["average_consistency"] or 0.0, 2)
            }
        else:
            summary = {
                "tests_count": 0,
                "practice_seconds": 0,
                "average_wpm": 0.0,
                "best_wpm": 0.0,
                "average_accuracy": 0.0,
                "best_accuracy": 0.0,
                "total_characters": 0,
                "total_errors": 0,
                "xp_earned": 0,
                "average_consistency": 0.0
            }
        
        summary["growth"] = self._calculate_growth(summary["average_wpm"], prev_average_wpm)

        # Build daily series sequence
        days_list = []
        for i in range(30):
            current_dt = start_dt + timedelta(days=i)
            curr_str = current_dt.strftime("%Y-%m-%d")
            
            if curr_str in db_days:
                days_list.append(db_days[curr_str])
            else:
                days_list.append({
                    "date": curr_str,
                    "tests_count": 0,
                    "practice_seconds": 0,
                    "average_wpm": 0.0,
                    "best_wpm": 0.0,
                    "average_accuracy": 0.0,
                    "best_accuracy": 0.0,
                    "total_characters": 0,
                    "total_errors": 0,
                    "xp_earned": 0,
                    "average_consistency": 0.0
                })

        return {
            "summary": summary,
            "days": days_list
        }
