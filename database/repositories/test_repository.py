"""
Test results database repository for TypeMaster.
"""
from datetime import datetime
from database.repositories.base_repository import BaseRepository

class TestRepository(BaseRepository):
    """
    Handles database operations for the session tests table.
    """
    def save_test(self, user_id: int, mode: str, duration: int, language: str,
                  wpm: float, raw_wpm: float, accuracy: float, characters: int,
                  correct_characters: int, incorrect_characters: int,
                  started_at: str = None, completed_at: str = None,
                  xp_earned: int = 0, is_pb: bool = False, difficulty: str = "normal",
                  consistency: float = None) -> int:
        """
        Inserts a completed typing test record into the database.
        Returns the primary key ID of the newly created row.
        """
        if not completed_at:
            completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
            INSERT INTO tests (
                user_id, started_at, completed_at, mode, duration, language, difficulty,
                wpm, raw_wpm, accuracy, characters, correct_characters, incorrect_characters,
                xp_earned, is_personal_best, consistency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        is_pb_val = 1 if is_pb else 0

        return self.execute_write(query, (
            user_id, started_at, completed_at, mode, duration, language, difficulty,
            wpm, raw_wpm, accuracy, characters, correct_characters, incorrect_characters,
            xp_earned, is_pb_val, consistency
        ), use_transaction=True)

    def get_tests_by_user(self, user_id: int, mode: str = None, difficulty: str = None,
                         only_pb: bool = False, limit: int = 50, offset: int = 0) -> list:
        """
        Retrieves a list of completed test runs for a user, with optional filters for mode,
        difficulty, and personal best status, sorted by completion date descending.
        """
        query = """
            SELECT id, user_id, started_at, completed_at, mode, duration, language, difficulty,
                   wpm, raw_wpm, accuracy, characters, correct_characters, incorrect_characters,
                   xp_earned, is_personal_best, consistency
            FROM tests
            WHERE user_id = ?
        """
        params = [user_id]

        if mode and mode != "Barchasi":
            query += " AND mode = ?"
            params.append(mode)

        if difficulty and difficulty != "Barchasi":
            query += " AND difficulty = ?"
            params.append(difficulty)

        if only_pb:
            query += " AND is_personal_best = 1"

        query += " ORDER BY completed_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return self.execute_query(query, params)

    def get_advanced_stats(self, user_id: int) -> dict:
        """
        Compiles advanced performance statistics, trends, level classification,
        and time of day habits of a user from their typing tests history.
        """
        # 1. Lifetime averages
        all_time_query = """
            SELECT 
                COUNT(*) as total_tests,
                SUM(duration) as total_duration,
                AVG(wpm) as avg_wpm,
                MAX(wpm) as max_wpm,
                AVG(accuracy) as avg_accuracy,
                AVG(consistency) as avg_consistency,
                SUM(characters) as total_characters,
                SUM(incorrect_characters) as total_errors,
                SUM(correct_characters) as total_correct
            FROM tests
            WHERE user_id = ?
        """
        
        # 2. Last 10 tests trend averages
        last_10_query = """
            SELECT wpm, accuracy, consistency
            FROM tests
            WHERE user_id = ?
            ORDER BY completed_at DESC
            LIMIT 10
        """

        # 3. All test hours for daily habit analysis
        hours_query = """
            SELECT strftime('%H', completed_at) as hour
            FROM tests
            WHERE user_id = ?
        """
        
        lifetime_rows = self.execute_query(all_time_query, (user_id,))
        lifetime_row = lifetime_rows[0] if lifetime_rows else None
        
        if not lifetime_row or not lifetime_row["total_tests"] or lifetime_row["total_tests"] == 0:
            return {
                "total_tests": 0,
                "total_duration": 0,
                "avg_wpm": 0.0,
                "max_wpm": 0.0,
                "avg_accuracy": 0.0,
                "avg_consistency": 0.0,
                "total_characters": 0,
                "total_errors": 0,
                "cumulative_accuracy": 0.0,
                "last_10_avg_wpm": 0.0,
                "last_10_avg_accuracy": 0.0,
                "last_10_avg_consistency": 0.0,
                "time_of_day_habit": "evening",
                "typing_rank": "beginner"
            }

        total_tests = lifetime_row["total_tests"] or 0
        total_duration = lifetime_row["total_duration"] or 0
        avg_wpm = round(lifetime_row["avg_wpm"] or 0.0, 2)
        max_wpm = round(lifetime_row["max_wpm"] or 0.0, 2)
        avg_accuracy = round(lifetime_row["avg_accuracy"] or 0.0, 2)
        avg_consistency = round(lifetime_row["avg_consistency"] or 0.0, 2)
        total_characters = lifetime_row["total_characters"] or 0
        total_errors = lifetime_row["total_errors"] or 0
        total_correct = lifetime_row["total_correct"] or 0
        
        cumulative_accuracy = 0.0
        if total_characters > 0:
            cumulative_accuracy = round((total_correct * 100.0) / total_characters, 2)

        last_10_rows = self.execute_query(last_10_query, (user_id,))
        
        last_10_avg_wpm = 0.0
        last_10_avg_accuracy = 0.0
        last_10_avg_consistency = 0.0
        
        if last_10_rows:
            count_10 = len(last_10_rows)
            sum_wpm = sum(r["wpm"] or 0.0 for r in last_10_rows)
            sum_acc = sum(r["accuracy"] or 0.0 for r in last_10_rows)
            sum_cons = sum(r["consistency"] or 0.0 for r in last_10_rows)
            last_10_avg_wpm = round(sum_wpm / count_10, 2)
            last_10_avg_accuracy = round(sum_acc / count_10, 2)
            last_10_avg_consistency = round(sum_cons / count_10, 2)

        hour_rows = self.execute_query(hours_query, (user_id,))
        
        time_blocks = {
            "morning": 0,    # 06:00 - 11:59
            "afternoon": 0,  # 12:00 - 17:59
            "evening": 0,    # 18:00 - 23:59
            "night": 0       # 00:00 - 05:59
        }
        
        for r in hour_rows:
            try:
                hr = int(r["hour"])
            except (ValueError, TypeError):
                continue
            if 6 <= hr < 12:
                time_blocks["morning"] += 1
            elif 12 <= hr < 18:
                time_blocks["afternoon"] += 1
            elif 18 <= hr < 24:
                time_blocks["evening"] += 1
            else:
                time_blocks["night"] += 1
        
        fav_block = max(time_blocks, key=time_blocks.get) if hour_rows else "evening"
        
        if avg_wpm < 25.0:
            typing_rank = "beginner"
        elif avg_wpm < 45.0:
            typing_rank = "intermediate"
        elif avg_wpm < 65.0:
            typing_rank = "pro"
        elif avg_wpm < 85.0:
            typing_rank = "master"
        else:
            typing_rank = "typemaster"
            
        return {
            "total_tests": total_tests,
            "total_duration": total_duration,
            "avg_wpm": avg_wpm,
            "max_wpm": max_wpm,
            "avg_accuracy": avg_accuracy,
            "avg_consistency": avg_consistency,
            "total_characters": total_characters,
            "total_errors": total_errors,
            "cumulative_accuracy": cumulative_accuracy,
            "last_10_avg_wpm": last_10_avg_wpm,
            "last_10_avg_accuracy": last_10_avg_accuracy,
            "last_10_avg_consistency": last_10_avg_consistency,
            "time_of_day_habit": fav_block,
            "typing_rank": typing_rank
        }


