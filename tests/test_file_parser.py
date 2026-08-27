import unittest
import os
import tempfile
from services.file_parser import extract_typing_text
from engine.test_config import TestConfig
from engine.typing_engine import TypingEngine

class TestFileParser(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_text_file_extraction(self):
        # Create a temp txt file
        file_path = os.path.join(self.temp_dir.name, "test.txt")
        words = ["hello", "world", "typing", "practice", "expert"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(" ".join(words))
            
        extracted = extract_typing_text(file_path, max_words=3)
        self.assertEqual(extracted, "hello world typing")
        
        # Test full extraction
        extracted_all = extract_typing_text(file_path, max_words=10)
        self.assertEqual(extracted_all, "hello world typing practice expert")

    def test_test_config_file_bypass(self):
        # Normal languages work
        config = TestConfig("English", 60)
        self.assertEqual(config.language, "English")
        
        # Bypasses for File label
        config_custom = TestConfig("Fayl: test_file.docx", 60)
        self.assertEqual(config_custom.language, "Fayl: test_file.docx")
        
        # Normal other strings still raise error
        with self.assertRaises(ValueError):
            TestConfig("Spanish", 60)

    def test_typing_engine_custom_text(self):
        config = TestConfig("English", 60)
        custom_prompt = "custom typing text sequence"
        
        # If custom_text supplied, engine target matches it
        engine = TypingEngine(config, custom_text=custom_prompt)
        self.assertEqual(engine.target_text, custom_prompt)
        
        # Default behavior compiles random text
        engine_default = TypingEngine(config)
        self.assertNotEqual(engine_default.target_text, custom_prompt)
        self.assertTrue(len(engine_default.target_text) > 0)
