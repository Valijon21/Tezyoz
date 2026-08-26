"""
Daily missions service module for TypeMaster.
Predefines mission templates, generates 3 daily random missions, updates progress, and awards rewards.
"""
import random
import logging
from datetime import datetime
from database.connection import db

logger = logging.getLogger("services.daily_missions_service")

TEMPLATES = [
    {
        "key": "practice_3_tests",
        "title": "Mashq qiluvchi",
        "description": "Bugun 3 ta yozish mashqini yakunlang",
        "target": 3,
        "xp_reward": 30
    },
    {
        "key": "wpm_50",
        "title": "Tezkor barmoqlar",
        "description": "Mashq qilganda kamida 50 WPM tezlikka erishing",
        "target": 1,
        "xp_reward": 40
    },
    {
        "key": "accuracy_97",
        "title": "Aniq mergan",
        "description": "Mashq qilganda kamida 97% aniqlikka erishing",
        "target": 1,
        "xp_reward": 40
    },
    {
        "key": "time_120",
        "title": "Vaqt sarflovchi",
        "description": "Bugun jami 120 soniya yozish mashqini bajaring",
        "target": 120,
        "xp_reward": 50
    },
    {
        "key": "accuracy_100",
        "title": "Mukammallik",
        "description": "Mashqni 100% aniqlikda yakunlang",
        "target": 1,
        "xp_reward": 50
    }
]

class DailyMissionsService:
    """
    Manages daily mission workflows, progress evaluations, and database synchronization.
    """
    def get_or_generate_daily_missions(self, user_id: int, date_str: str) -> list[dict]:
        """
        Loads the daily missions for user on a target date, generating them if not present.
        """
        query = """
            SELECT id, user_id, date, mission_key, title, description, progress, target, xp_reward, completed
            FROM user_daily_missions
            WHERE user_id = ? AND date = ?
            ORDER BY id ASC;
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(query, (user_id, date_str))
                rows = cursor.fetchall()
                missions = [dict(r) for r in rows]

            if len(missions) >= 3:
                return missions

            # Generate new unique missions for today
            chosen_templates = random.sample(TEMPLATES, 3)
            generated = []
            
            with db.transaction() as conn:
                # Double-check inside transaction to avoid race conditions
                cursor = conn.execute(query, (user_id, date_str))
                rows = cursor.fetchall()
                if len(rows) >= 3:
                    return [dict(r) for r in rows]

                for temp in chosen_templates:
                    conn.execute("""
                        INSERT INTO user_daily_missions (user_id, date, mission_key, title, description, progress, target, xp_reward, completed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0);
                    """, (user_id, date_str, temp["key"], temp["title"], temp["description"], 0, temp["target"], temp["xp_reward"]))
                
                # Retrieve fully initialized rows
                cursor = conn.execute(query, (user_id, date_str))
                generated = [dict(r) for r in cursor.fetchall()]
            
            return generated
        except Exception as e:
            logger.error(f"Error fetching/generating daily missions for user {user_id} on {date_str}: {e}", exc_info=True)
            return []

    def update_mission_progress(self, user_id: int, date_str: str, wpm: float, accuracy: float, duration: int) -> list[dict]:
        """
        Increments progress for all active missions of a user on a given date.
        If a mission targets are met, awards rewards, sets completed states, and triggers session syncs.
        """
        query = """
            SELECT id, mission_key, title, description, progress, target, xp_reward, completed
            FROM user_daily_missions
            WHERE user_id = ? AND date = ? AND completed = 0;
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(query, (user_id, date_str))
                active_missions = [dict(r) for r in cursor.fetchall()]

            if not active_missions:
                return []

            newly_completed = []

            with db.transaction() as conn:
                for mission in active_missions:
                    m_id = mission["id"]
                    key = mission["mission_key"]
                    prog = mission["progress"]
                    tgt = mission["target"]
                    xp_reward = mission["xp_reward"]
                    
                    new_prog = prog
                    if key == "practice_3_tests":
                        new_prog = min(prog + 1, tgt)
                    elif key == "wpm_50":
                        if wpm >= 50.0:
                            new_prog = 1
                    elif key == "accuracy_97":
                        if accuracy >= 97.0:
                            new_prog = 1
                    elif key == "time_120":
                        new_prog = min(prog + duration, tgt)
                    elif key == "accuracy_100":
                        if accuracy == 100.0:
                            new_prog = 1

                    if new_prog != prog:
                        # Write progress back
                        conn.execute("UPDATE user_daily_missions SET progress = ? WHERE id = ?;", (new_prog, m_id))

                    if new_prog >= tgt:
                        # Mark completed
                        conn.execute("UPDATE user_daily_missions SET completed = 1 WHERE id = ?;", (m_id,))
                        
                        # Award XP to user inside the same transaction
                        conn.execute("UPDATE users SET xp = xp + ? WHERE id = ?;", (xp_reward, user_id))
                        
                        # Recalculate level on award
                        cursor_xp = conn.execute("SELECT xp FROM users WHERE id = ?;", (user_id,))
                        updated_row = cursor_xp.fetchone()
                        updated_xp = updated_row["xp"] if updated_row else xp_reward
                        
                        from gamification.levels import calculate_level
                        new_lvl = calculate_level(updated_xp)
                        conn.execute("UPDATE users SET level = ? WHERE id = ?;", (new_lvl, user_id))

                        newly_completed.append({
                            "key": key,
                            "title": mission["title"],
                            "description": mission["description"],
                            "xp_reward": xp_reward
                        })

            if newly_completed:
                from services.auth_service import refresh_current_user
                refresh_current_user()

            return newly_completed
        except Exception as e:
            logger.error(f"Error updating daily missions for user {user_id}: {e}", exc_info=True)
            return []
