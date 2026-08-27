"""
Unit tests for TypeMaster ResultsView.
Verifies layout initialization, metric cards update values, and button callbacks.
"""
import unittest
import tkinter as tk
from tkinter import ttk
from ui.results import ResultsView

from app.event_bus import EventBus

class MockApplication:
    """Mock main container controller to track route changes."""
    def __init__(self):
        self.shown_view = None
        self.event_bus = EventBus()

    def show_view(self, view_name: str):
        self.shown_view = view_name


class TestResultsUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = MockApplication()
        self.view = ResultsView(self.root, self.app)

    def tearDown(self):
        self.view.destroy()
        self.root.destroy()

    def test_results_layout_initialization(self):
        """Verify that UI panels and cards structure load correctly."""
        # Check header title exists
        self.assertEqual(self.view.title_label.cget("text"), "Mashq Natijalari")
        
        # Check cards are loaded inside metrics dictionary mapping references
        self.assertIn("wpm", self.view.cards)
        self.assertIn("raw_wpm", self.view.cards)
        self.assertIn("accuracy", self.view.cards)
        self.assertIn("errors", self.view.cards)
        self.assertIn("duration", self.view.cards)
        self.assertIn("xp_level", self.view.cards)

    def test_set_results_updates_values(self):
        """Verify set_results sets text values on metric card labels correctly."""
        # Call results mapping loader
        # wpm=45.5, raw_wpm=48.0, accuracy=94.5, errors=3, duration=60, xp=12, level=3, is_pb=True, streak=5, longest_streak=10
        self.view.set_results(
            wpm=45.5,
            raw_wpm=48.0,
            accuracy=94.5,
            errors=3,
            duration=60,
            xp_earned=12,
            level=3,
            is_pb=True,
            streak=5,
            longest_streak=10
        )

        # Check values mappings matches suffix and precision specs
        self.assertEqual(self.view.cards["wpm"]["label"].cget("text"), "45.5")
        self.assertEqual(self.view.cards["raw_wpm"]["label"].cget("text"), "48.0")
        self.assertEqual(self.view.cards["accuracy"]["label"].cget("text"), "94.5%")
        self.assertEqual(self.view.cards["errors"]["label"].cget("text"), "3")
        self.assertEqual(self.view.cards["duration"]["label"].cget("text"), "60 soniya")
        self.assertEqual(self.view.cards["xp_level"]["label"].cget("text"), "+12 XP (Lvl 3)")

        # Verify PB badge is packed and visible
        self.assertEqual(self.view.pb_badge.winfo_manager(), "pack")

        # Verify Streak badge is packed and visible
        self.assertEqual(self.view.streak_badge.winfo_manager(), "pack")
        self.assertEqual(self.view.streak_badge.cget("text"), "Joriy Streak: 5 kun 🔥")

    def test_pb_badge_visibility_toggle(self):
        """Verify PB badge packs and unpacks dynamically based on is_pb bool state."""
        # If not pb
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, is_pb=False)
        self.assertEqual(self.view.pb_badge.winfo_manager(), "")

        # If pb
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, is_pb=True)
        self.assertEqual(self.view.pb_badge.winfo_manager(), "pack")

    def test_streak_badge_visibility_and_pb(self):
        """Verify streak badge packs, unpacks, and highlights record streaks dynamically."""
        # 1. Streak is 0 -> should not display
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, streak=0)
        self.assertEqual(self.view.streak_badge.winfo_manager(), "")

        # 2. Streak > 0 but not personal best -> should display standard text
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, streak=3, longest_streak=5)
        self.assertEqual(self.view.streak_badge.winfo_manager(), "pack")
        self.assertEqual(self.view.streak_badge.cget("text"), "Joriy Streak: 3 kun 🔥")
        self.assertEqual(str(self.view.streak_badge.cget("foreground")), "#f59e0b")

        # 3. Streak >= longest_streak -> should display new record text and darker highlight
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, streak=6, longest_streak=5)
        self.assertEqual(self.view.streak_badge.winfo_manager(), "pack")
        self.assertEqual(self.view.streak_badge.cget("text"), "★ YANGI REKORD STREAK: 6 kun 🔥 ★")
        self.assertEqual(str(self.view.streak_badge.cget("foreground")), "#ea580c")

    def test_navigation_buttons(self):
        """Verify navigation buttons trigger routing actions on the controller."""
        # Retry click button action mapping
        self.view.retry_btn.invoke()
        self.assertEqual(self.app.shown_view, "typing_test")

        # Home click button action mapping
        self.app.shown_view = None
        self.view.home_btn.invoke()
        self.assertEqual(self.app.shown_view, "home")


if __name__ == '__main__':
    unittest.main()
