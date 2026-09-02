"""
Achievements service module for TypeMaster.
Provides logic for querying, checking, and awarding achievements with transactional safety.
"""
import logging
from datetime import datetime
from database.connection import db

logger = logging.getLogger("services.achievements_service")

class AchievementsService:
    """
    Handles business logic for evaluating, awarding, and retrieving user achievements.
    """
    def get_all_achievements(self, user_id: int) -> list[dict]:
        """
        Retrieves all registered achievements in the system, with details on whether
        the specified user has unlocked them.
        """
        query = """
            SELECT a.id, a.key, a.title, a.description, a.xp_reward, ua.unlocked_at
            FROM achievements a
            LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = ?
            ORDER BY a.id ASC;
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(query, (user_id,))
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch achievements for user {user_id}: {e}")
            return []

    def check_and_award_achievements(self, user_id: int) -> list[dict]:
        """
        Checks milestones for the user and awards any newly unlocked achievements.
        Returns a list of newly unlocked achievement dictionaries.
        """
        try:
            # 1. Query metrics from database
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as tests_count, 
                        COALESCE(MAX(wpm), 0) as max_wpm,
                        COALESCE((SELECT COUNT(*) FROM tests WHERE user_id = ? AND accuracy = 100.0 AND duration >= 30), 0) as accuracy_100_count,
                        COALESCE((SELECT COUNT(*) FROM tests WHERE user_id = ? AND mode = 'smart_practice'), 0) as smart_practice_count
                    FROM tests 
                    WHERE user_id = ?;
                """, (user_id, user_id, user_id))
                tests_row = cursor.fetchone()
                
                cursor = conn.execute("SELECT current_streak, level FROM users WHERE id = ?;", (user_id,))
                user_row = cursor.fetchone()

            if not tests_row or not user_row:
                return []

            tests_count = tests_row["tests_count"]
            max_wpm = tests_row["max_wpm"]
            accuracy_100_count = tests_row["accuracy_100_count"]
            smart_practice_count = tests_row["smart_practice_count"]
            current_streak = user_row["current_streak"]
            level = user_row["level"]

            # 2. Map milestones to achievements keys
            qualifies = []
            if tests_count >= 1:
                qualifies.append("first_test")
            if tests_count >= 10:
                qualifies.append("tests_10")
            if tests_count >= 50:
                qualifies.append("tests_50")
            if tests_count >= 100:
                qualifies.append("tests_100")

            if max_wpm >= 40:
                qualifies.append("speed_40")
            if max_wpm >= 60:
                qualifies.append("speed_60")
            if max_wpm >= 80:
                qualifies.append("speed_80")
            if max_wpm >= 100:
                qualifies.append("speed_100")
            if max_wpm >= 120:
                qualifies.append("speed_120")

            if accuracy_100_count >= 1:
                qualifies.append("accuracy_100")
            if smart_practice_count >= 5:
                qualifies.append("smart_practice_5")

            if current_streak >= 3:
                qualifies.append("streak_3")
            if current_streak >= 7:
                qualifies.append("streak_7")
            if current_streak >= 14:
                qualifies.append("streak_14")
            if current_streak >= 30:
                qualifies.append("streak_30")

            if level >= 5:
                qualifies.append("level_5")
            if level >= 10:
                qualifies.append("level_10")

            if not qualifies:
                return []

            newly_unlocked = []

            # 3. Check and award achievements in transaction
            with db.transaction() as conn:
                # Query achievements keys already unlocked by this user
                cursor = conn.execute("""
                    SELECT a.key 
                    FROM user_achievements ua
                    JOIN achievements a ON ua.achievement_id = a.id
                    WHERE ua.user_id = ?;
                """, (user_id,))
                unlocked_keys = {row["key"] for row in cursor.fetchall()}

                for key in qualifies:
                    if key not in unlocked_keys:
                        # Fetch achievement details
                        cursor = conn.execute("SELECT id, title, description, xp_reward FROM achievements WHERE key = ?;", (key,))
                        ach_row = cursor.fetchone()
                        if ach_row:
                            ach_id = ach_row["id"]
                            xp_reward = ach_row["xp_reward"]

                            # Unlock achievement
                            conn.execute("""
                                INSERT INTO user_achievements (user_id, achievement_id)
                                VALUES (?, ?);
                            """, (user_id, ach_id))

                            # Award XP and update level to user
                            conn.execute("UPDATE users SET xp = xp + ? WHERE id = ?;", (xp_reward, user_id))
                            cursor_xp = conn.execute("SELECT xp FROM users WHERE id = ?;", (user_id,))
                            updated_row = cursor_xp.fetchone()
                            updated_xp = updated_row["xp"] if updated_row else xp_reward
                            
                            from gamification.levels import calculate_level
                            new_lvl = calculate_level(updated_xp)
                            conn.execute("UPDATE users SET level = ? WHERE id = ?;", (new_lvl, user_id))

                            newly_unlocked.append({
                                "key": key,
                                "title": ach_row["title"],
                                "description": ach_row["description"],
                                "xp_reward": xp_reward
                            })

            # Refresh local user session stats to show updated XP & level
            if newly_unlocked:
                from services.auth_service import refresh_current_user
                refresh_current_user()

            return newly_unlocked

        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}", exc_info=True)
            return []
