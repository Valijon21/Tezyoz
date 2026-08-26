"""
Gamification services and XP calculator engine for TypeMaster.
"""
from app.config import (
    XP_TEST_COMPLETED,
    XP_ACCURACY_95,
    XP_ACCURACY_98,
    XP_PERSONAL_BEST
)

def calculate_test_xp(duration_seconds: int, accuracy: float, is_pb: bool) -> int:
    """
    Calculates total XP earned for completing a typing test.
    XP consists of:
    - Base Completed Test XP (flat rate from configuration)
    - Duration Scaling XP (duration / 15 seconds)
    - Accuracy milestones (>=95% grants +20 XP, >=98% grants +40 XP)
    - Personal Best bonus (grants +100 XP)
    """
    # Flat base reward for completion
    total_xp = XP_TEST_COMPLETED

    # Duration scaling (15s = 1, 30s = 2, 60s = 4, 120s = 8)
    duration_xp = duration_seconds // 15
    total_xp += duration_xp

    # Accuracy bonuses
    if accuracy >= 98.0:
        total_xp += XP_ACCURACY_98
    elif accuracy >= 95.0:
        total_xp += XP_ACCURACY_95

    # Personal Best bonus
    if is_pb:
        total_xp += XP_PERSONAL_BEST

    return total_xp
