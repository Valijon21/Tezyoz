"""
Unit tests for TypeMaster progressive level system formulas.
"""
import unittest
from gamification.levels import calculate_level, get_level_progress

class TestLevelSystem(unittest.TestCase):
    def test_calculate_level(self):
        """Verify calculate_level returns correct progressive level thresholds."""
        # Level 1 boundaries: 0 - 99 XP
        self.assertEqual(calculate_level(-50), 1)
        self.assertEqual(calculate_level(0), 1)
        self.assertEqual(calculate_level(50), 1)
        self.assertEqual(calculate_level(99), 1)
        
        # Level 2 boundaries: 100 - 299 XP (needs 200)
        self.assertEqual(calculate_level(100), 2)
        self.assertEqual(calculate_level(150), 2)
        self.assertEqual(calculate_level(299), 2)
        
        # Level 3 boundaries: 300 - 599 XP (needs 300)
        self.assertEqual(calculate_level(300), 3)
        self.assertEqual(calculate_level(450), 3)
        self.assertEqual(calculate_level(599), 3)
        
        # Level 4 boundaries: 600 - 999 XP (needs 400)
        self.assertEqual(calculate_level(600), 4)
        self.assertEqual(calculate_level(999), 4)
        
        # Level 5 boundaries: 1000+ XP (needs 500)
        self.assertEqual(calculate_level(1000), 5)
        self.assertEqual(calculate_level(1499), 5)
        self.assertEqual(calculate_level(1500), 6)

    def test_get_level_progress(self):
        """Verify get_level_progress yields correct level progress and requirements."""
        # Level 1 progress
        self.assertEqual(get_level_progress(-20), (1, 0, 100))
        self.assertEqual(get_level_progress(0), (1, 0, 100))
        self.assertEqual(get_level_progress(50), (1, 50, 100))
        self.assertEqual(get_level_progress(99), (1, 99, 100))
        
        # Level 2 progress
        self.assertEqual(get_level_progress(100), (2, 0, 200))
        self.assertEqual(get_level_progress(150), (2, 50, 200))
        self.assertEqual(get_level_progress(299), (2, 199, 200))
        
        # Level 3 progress
        self.assertEqual(get_level_progress(300), (3, 0, 300))
        self.assertEqual(get_level_progress(450), (3, 150, 300))
        self.assertEqual(get_level_progress(599), (3, 299, 300))
        
        # Level 4 progress
        self.assertEqual(get_level_progress(600), (4, 0, 400))
        self.assertEqual(get_level_progress(850), (4, 250, 400))
        
        # Level 5 progress
        self.assertEqual(get_level_progress(1000), (5, 0, 500))
