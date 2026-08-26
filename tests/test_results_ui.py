"""
Unit tests for TypeMaster ResultsView.
Verifies layout initialization, metric cards update values, and button callbacks.
"""
import unittest
import tkinter as tk
from tkinter import ttk
from ui.results import ResultsView

class MockApplication:
    """Mock main container controller to track route changes."""
    def __init__(self):
        self.shown_view = None

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
        # wpm=45.5, raw_wpm=48.0, accuracy=94.5, errors=3, duration=60, xp=12, level=3, is_pb=True
        self.view.set_results(
            wpm=45.5,
            raw_wpm=48.0,
            accuracy=94.5,
            errors=3,
            duration=60,
            xp_earned=12,
            level=3,
            is_pb=True
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

    def test_pb_badge_visibility_toggle(self):
        """Verify PB badge packs and unpacks dynamically based on is_pb bool state."""
        # If not pb
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, is_pb=False)
        self.assertEqual(self.view.pb_badge.winfo_manager(), "")

        # If pb
        self.view.set_results(40, 40, 100, 0, 30, 5, 2, is_pb=True)
        self.assertEqual(self.view.pb_badge.winfo_manager(), "pack")

    def test_navigation_buttons(self):
        """Verify navigation buttons trigger routing actions on the controller."""
        # Retry click button action mapping
        self.view.retry_btn.invoke()
        self.assertEqual(self.app.shown_view, "home")

        # Home click button action mapping
        self.app.shown_view = None
        self.view.home_btn.invoke()
        self.assertEqual(self.app.shown_view, "home")

if __name__ == '__main__':
    unittest.main()
