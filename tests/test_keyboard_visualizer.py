"""
Unit tests for KeyboardVisualizer component and key helper functionalities.
"""
import unittest
import tkinter as tk
import customtkinter as ctk
from unittest.mock import MagicMock
from ui.keyboard_visualizer import KeyboardVisualizer, KEY_MAP, FINGER_MAP
from ui.theme import THEMES

class TestKeyboardVisualizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need a root window for Tkinter widgets initialization
        cls.root = ctk.CTk()
        cls.root.withdraw() # Hide the window

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_key_mappings(self):
        # Verify basic mappings are populated
        self.assertEqual(KEY_MAP['a'], 'A')
        self.assertEqual(KEY_MAP['A'], 'A')
        self.assertEqual(KEY_MAP[' '], 'SPACE')
        self.assertEqual(KEY_MAP['\n'], 'ENTER')
        self.assertEqual(KEY_MAP['1'], '1')
        self.assertEqual(KEY_MAP['!'], '1')

    def test_finger_mappings(self):
        # Verify finger recommendations
        self.assertEqual(FINGER_MAP[' '], 'finger_thumb')
        self.assertEqual(FINGER_MAP['f'], 'finger_left_index')
        self.assertEqual(FINGER_MAP['j'], 'finger_right_index')
        self.assertEqual(FINGER_MAP['a'], 'finger_left_pinky')
        self.assertEqual(FINGER_MAP['p'], 'finger_right_pinky')

    def test_visualizer_initialization_and_highlight(self):
        mock_controller = MagicMock()
        mock_controller.current_theme = "dark"
        
        visualizer = KeyboardVisualizer(self.root, mock_controller)
        self.assertIsNotNone(visualizer)
        
        # Test key highlight logic
        visualizer.highlight_key('a')
        self.assertIn('A', visualizer.highlighted_keys)
        # 'a' is lowercase, should not highlight shift keys
        self.assertNotIn('LSHIFT', visualizer.highlighted_keys)
        self.assertNotIn('RSHIFT', visualizer.highlighted_keys)
        
        visualizer.highlight_key('A')
        self.assertIn('A', visualizer.highlighted_keys)
        # 'A' is uppercase, should highlight a shift key
        self.assertTrue('LSHIFT' in visualizer.highlighted_keys or 'RSHIFT' in visualizer.highlighted_keys)

        # Highlight space
        visualizer.highlight_key(' ')
        self.assertIn('SPACE', visualizer.highlighted_keys)
        
        # Highlight None clears selection
        visualizer.highlight_key(None)
        self.assertEqual(len(visualizer.highlighted_keys), 0)

    def test_finger_tutor_bar_and_keypress(self):
        mock_controller = MagicMock()
        mock_controller.current_theme = "dark"
        
        visualizer = KeyboardVisualizer(self.root, mock_controller)
        
        # Verify finger shapes are created
        self.assertEqual(len(visualizer.finger_shapes), 10) # 8 fingers + 2 thumbs
        self.assertIn("finger_left_pinky", visualizer.finger_shapes)
        
        # Test tutor bar highlights on key highlight
        visualizer.highlight_key('a')
        
        # Left pinky shape should be filled with the theme's accent color
        theme_colors = THEMES.get("dark")
        shape_id = visualizer.finger_shapes["finger_left_pinky"]
        fill_color = visualizer.hand_canvas.itemcget(shape_id, "fill")
        self.assertEqual(fill_color, theme_colors["accent"])
        
        # Test visualize_press key modification
        visualizer.visualize_press('q')
        q_widget = visualizer.key_widgets['Q']
        self.assertEqual(q_widget.cget("fg_color"), "#10b981") # pressed color for dark theme
        
        # Manually invoke restore to simulate timeout
        visualizer.restore_key_color('Q')
        self.assertNotEqual(q_widget.cget("fg_color"), "#10b981")

    def test_russian_layout_mapping(self):
        mock_controller = MagicMock()
        mock_controller.current_theme = "dark"
        
        visualizer = KeyboardVisualizer(self.root, mock_controller)
        
        # Default is English
        self.assertEqual(visualizer.key_widgets['Q'].cget('text'), "Q")
        
        # Switch to Russian
        visualizer.set_practice_language("Russian")
        self.assertEqual(visualizer.key_widgets['Q'].cget('text'), "Й")
        
        # Highlight Cyrillic 'й'
        visualizer.highlight_key('й')
        self.assertIn('Q', visualizer.highlighted_keys)
        
        # Left pinky shape should be filled with the theme's accent color
        theme_colors = THEMES.get("dark")
        shape_id = visualizer.finger_shapes["finger_left_pinky"]
        fill_color = visualizer.hand_canvas.itemcget(shape_id, "fill")
        self.assertEqual(fill_color, theme_colors["accent"])
        
        # Switch back to English
        visualizer.set_practice_language("English")
        self.assertEqual(visualizer.key_widgets['Q'].cget('text'), "Q")

if __name__ == '__main__':
    unittest.main()
