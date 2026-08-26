"""
Progressive leveling calculations and helpers for TypeMaster.
"""

def calculate_level(total_xp: int) -> int:
    """
    Calculates user level based on cumulative XP using progressive scaling.
    Level 1: 0 - 99 XP
    Level 2: 100 - 299 XP (needs 200 XP to reach Level 3)
    Level 3: 300 - 599 XP (needs 300 XP to reach Level 4)
    Level N: needs N * 100 XP to reach Level N+1.
    """
    if total_xp < 0:
        total_xp = 0
    level = 1
    while total_xp >= level * 100:
        total_xp -= level * 100
        level += 1
    return level

def get_level_progress(total_xp: int) -> tuple[int, int, int]:
    """
    Given total cumulative XP, returns:
    (current_level, xp_in_current_level, xp_needed_for_next_level)
    """
    if total_xp < 0:
        total_xp = 0
    level = 1
    remaining_xp = total_xp
    while remaining_xp >= level * 100:
        remaining_xp -= level * 100
        level += 1
    return level, remaining_xp, level * 100
