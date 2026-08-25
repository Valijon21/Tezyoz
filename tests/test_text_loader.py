"""
Unit tests for TypeMaster Text Loader engine.
Verifies static dictionary load successes, missing assets fallbacks, and normalizing inputs casing.
"""
import unittest
import tempfile
import os
from pathlib import Path
import engine.text_loader as loader
from engine.text_loader import load_words_for_language, DEFAULT_ENGLISH_WORDS

class TestTextLoader(unittest.TestCase):
    def test_load_words_english_success(self):
        """Verify english wordlist loads correctly from file and returns list of strings."""
        words = load_words_for_language("English")
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 50)
        self.assertEqual(words[0], "the")

    def test_load_words_russian_success(self):
        """Verify russian wordlist loads correctly from file and returns list."""
        words = load_words_for_language("Russian")
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 50)
        self.assertEqual(words[0], "и")

    def test_load_words_uzbek_success(self):
        """Verify uzbek wordlist loads correctly from file."""
        words = load_words_for_language("Uzbek")
        self.assertIsInstance(words, list)
        self.assertGreater(len(words), 50)
        self.assertEqual(words[0], "va")

    def test_load_words_fallback_on_missing_file(self):
        """Verify default language backup lists are loaded for non-existent target files without tracebacks."""
        # Non-existent language file
        words = load_words_for_language("Spanish")
        self.assertEqual(words, DEFAULT_ENGLISH_WORDS)

    def test_load_words_normalization(self):
        """Verify whitespace clearing and capitalization adjustments during lookup."""
        words_caps = load_words_for_language("  ENGLISH  ")
        words_low = load_words_for_language("english")
        self.assertEqual(words_caps, words_low)

    def test_load_words_invalid_input(self):
        """Verify passing None or non-string inputs returns default English wordlist."""
        words_none = load_words_for_language(None)
        self.assertEqual(words_none, DEFAULT_ENGLISH_WORDS)
        
        words_num = load_words_for_language(123)
        self.assertEqual(words_num, DEFAULT_ENGLISH_WORDS)

    def test_load_empty_or_broken_file_fallback(self):
        """Verify empty files default back to fallback memory lists."""
        temp_dir = tempfile.TemporaryDirectory()
        try:
            original_file = Path(loader.__file__)
            base_dir = original_file.resolve().parent.parent
            mock_file_path = base_dir / "assets" / "texts" / "mocklang.txt"
            
            # Write empty mock file
            with open(mock_file_path, "w", encoding="utf-8") as f:
                f.write("   \n   \t  ")
                
            words = load_words_for_language("mocklang")
            self.assertEqual(words, DEFAULT_ENGLISH_WORDS)
            
            # Clean up mock file
            if mock_file_path.exists():
                mock_file_path.unlink()
        finally:
            temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
