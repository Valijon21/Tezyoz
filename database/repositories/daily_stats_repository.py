"""
Daily statistics database repository for TypeMaster.
"""
from datetime import datetime, timedelta
from database.connection import db

class DailyStatsRepository:
    """
    Handles database operations for aggregating, upserting, and retrieving daily user stats.
    """
    def get_daily_stats(self, user_id: int, date_str: str) -> dict:
        """
        Retrieves aggregated stats for the specified user and date.
        If no record exists, returns a dictionary of default zero metrics.
        """
        query = """
            SELECT tests_count, practice_seconds, average_wpm, best_wpm,
                   average_accuracy, best_accuracy, total_characters, total_errors, xp_earned
            FROM daily_stats
            WHERE user_id = ? AND date = ?
        """
        with db.transaction() as conn:
            cursor = conn.execute(query, (user_id, date_str))
            row = cursor.fetchone()
            if row:
                return dict(row)

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
            "xp_earned": 0
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
                SUM(xp_earned) as total_xp
            FROM tests
            WHERE user_id = ? AND date(completed_at) = ?
        """

        upsert_query = """
            INSERT INTO daily_stats (
                user_id, date, tests_count, practice_seconds, average_wpm, best_wpm,
                average_accuracy, best_accuracy, total_characters, total_errors, xp_earned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                tests_count = excluded.tests_count,
                practice_seconds = excluded.practice_seconds,
                average_wpm = excluded.average_wpm,
                best_wpm = excluded.best_wpm,
                average_accuracy = excluded.average_accuracy,
                best_accuracy = excluded.best_accuracy,
                total_characters = excluded.total_characters,
                total_errors = excluded.total_errors,
                xp_earned = excluded.xp_earned
        """

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
                    "xp_earned": 0
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
                    "xp_earned": row["total_xp"] or 0
                }

            if tests_count > 0:
                conn.execute(upsert_query, (
                    user_id, date_str,
                    stats["tests_count"], stats["practice_seconds"],
                    stats["average_wpm"], stats["best_wpm"],
                    stats["average_accuracy"], stats["best_accuracy"],
                    stats["total_characters"], stats["total_errors"], stats["xp_earned"]
                ))

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
                SUM(xp_earned) as total_xp
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
        """

        # Query all existing daily stats in range
        days_query = """
            SELECT date, tests_count, practice_seconds, average_wpm, best_wpm,
                   average_accuracy, best_accuracy, total_characters, total_errors, xp_earned
            FROM daily_stats
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
        """

        with db.transaction() as conn:
            cursor = conn.execute(summary_query, (user_id, start_date_str, end_date_str))
            row = cursor.fetchone()
            
            cursor_days = conn.execute(days_query, (user_id, start_date_str, end_date_str))
            db_days = {r["date"]: dict(r) for r in cursor_days.fetchall()}

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
                "xp_earned": row["total_xp"]
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
                "xp_earned": 0
            }

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
                    "xp_earned": 0
                })

        return {
            "summary": summary,
            "days": days_list
        }
