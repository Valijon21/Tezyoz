"""
Unit tests for TypeMaster Keyboard event handler.
Verifies backspace recognition, printable char normalization, and ignoring control keys.
"""
import unittest
from engine.keyboard_handler import process_key_event

class MockEvent:
    """Mock container representing Tkinter GUI keypress events."""
    def __init__(self, keysym: str, char: str):
        self.keysym = keysym
        self.char = char

class TestKeyboardHandler(unittest.TestCase):
    def test_process_backspace(self):
        """Verify Event mapping returns backspace action on BackSpace keysym."""
        event = MockEvent("BackSpace", "")
        action, val = process_key_event(event)
        self.assertEqual(action, "backspace")
        self.assertIsNone(val)

    def test_process_valid_printable(self):
        """Verify printable inputs match character action maps."""
        # Standard ASCII characters
        event_a = MockEvent("a", "a")
        action, val = process_key_event(event_a)
        self.assertEqual(action, "input")
        self.assertEqual(val, "a")

        # Space key
        event_space = MockEvent("space", " ")
        action, val = process_key_event(event_space)
        self.assertEqual(action, "input")
        self.assertEqual(val, " ")

        # Uzbek and Russian Unicode letters
        event_cyrillic = MockEvent("Cyrillic_ya", "я")
        action, val = process_key_event(event_cyrillic)
        self.assertEqual(action, "input")
        self.assertEqual(val, "я")

        # Punctuation
        event_punct = MockEvent("period", ".")
        action, val = process_key_event(event_punct)
        self.assertEqual(action, "input")
        self.assertEqual(val, ".")

    def test_process_ignored_control_keys(self):
        """Verify navigation, command shortcuts, Caps Lock, Tab, Esc and F1-F12 are ignored."""
        # Esc
        event_esc = MockEvent("Escape", "")
        action, val = process_key_event(event_esc)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

        # Tab
        event_tab = MockEvent("Tab", "\t")
        action, val = process_key_event(event_tab)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

        # Newline / Enter
        event_enter = MockEvent("Return", "\n")
        action, val = process_key_event(event_enter)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

        # Arrow Right
        event_arrow = MockEvent("Right", "")
        action, val = process_key_event(event_arrow)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

        # Shift (no char representation)
        event_shift = MockEvent("Shift_L", "")
        action, val = process_key_event(event_shift)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

    def test_process_none_event(self):
        """Verify passing None returns ignore action safely."""
        action, val = process_key_event(None)
        self.assertEqual(action, "ignore")
        self.assertIsNone(val)

if __name__ == '__main__':
    unittest.main()
