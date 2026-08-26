"""
TypingEngine core state machine module for TypeMaster.
Manages user keystrokes buffers, calculates real-time metrics (WPM, Raw WPM, Accuracy),
observes active durations, and fires on-change event callbacks.
"""
import time
import random
from engine.test_config import TestConfig
from engine.text_loader import load_words_for_language

class TypingEngine:
    """Core state coordinator for active typing test practice sessions."""
    def __init__(self, config: TestConfig):
        self.config = config
        self.target_text = ""
        self.typed_text = ""
        self.total_typed_count = 0
        self.error_count = 0
        
        self.start_time = None
        self.end_time = None
        self.is_active = False
        self.is_finished = False
        
        self.callbacks = []
        self.compile_target_text()

    def compile_target_text(self):
        """Loads repository words and compiles a randomized typing prompt block."""
        words = load_words_for_language(self.config.language)
        # Select 250 random words from vocabulary
        selected = random.choices(words, k=250)
        self.target_text = " ".join(selected)

    def add_callback(self, callback):
        """Registers a listener callback function to execute on keystroke changes."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def _trigger_callbacks(self):
        """Triggers all registered listeners by passing self reference."""
        for cb in self.callbacks:
            try:
                cb(self)
            except Exception:
                pass

    def start_test(self):
        """Starts active test session timer."""
        self.is_active = True
        self.start_time = time.time()

    def complete_test(self):
        """Completes active typing practice, stopping timer."""
        self.is_active = False
        self.is_finished = True
        self.end_time = time.time()
        self._trigger_callbacks()

    def input_character(self, char: str):
        """
        Accepts a user typed input character.
        Starts session on first keypress, increments raw counter, and checks target correctness.
        """
        if self.is_finished:
            return
            
        if not self.is_active and not self.is_finished:
            self.start_test()
            
        if len(self.typed_text) >= len(self.target_text):
            return
            
        self.typed_text += char
        self.total_typed_count += 1
        
        # Check correctness of newly added character
        expected_char = self.target_text[len(self.typed_text) - 1]
        if char != expected_char:
            self.error_count += 1
            
        # Complete test if target boundary reached
        if len(self.typed_text) == len(self.target_text):
            self.complete_test()
        else:
            self._trigger_callbacks()

    def backspace(self):
        """Removes the last typed character if session is currently active."""
        if self.is_finished or not self.is_active:
            return
            
        if self.typed_text:
            self.typed_text = self.typed_text[:-1]
            self._trigger_callbacks()

    def tick(self):
        """Regularly checks if target configuration duration limit has elapsed."""
        if not self.is_active:
            return
            
        if self.get_elapsed_time() >= self.config.duration:
            self.complete_test()

    def get_elapsed_time(self) -> float:
        """Calculates current elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
            
        if self.is_finished:
            return self.end_time - self.start_time
            
        return time.time() - self.start_time

    def get_correct_characters_count(self) -> int:
        """Compares target and typed buffers to calculate current matching characters count."""
        correct_count = 0
        min_len = min(len(self.typed_text), len(self.target_text))
        for i in range(min_len):
            if self.typed_text[i] == self.target_text[i]:
                correct_count += 1
        return correct_count

    def get_wpm(self) -> float:
        """Calculates Net Words Per Minute."""
        elapsed_minutes = self.get_elapsed_time() / 60.0
        if elapsed_minutes <= 0:
            return 0.0
            
        correct_chars = self.get_correct_characters_count()
        return (correct_chars / 5.0) / elapsed_minutes

    def get_raw_wpm(self) -> float:
        """Calculates Raw Words Per Minute inclusive of errors."""
        elapsed_minutes = self.get_elapsed_time() / 60.0
        if elapsed_minutes <= 0:
            return 0.0
            
        return (self.total_typed_count / 5.0) / elapsed_minutes

    def get_accuracy(self) -> float:
        """Calculates typing accuracy percentage."""
        if self.total_typed_count == 0:
            return 0.0
            
        correct_chars = self.get_correct_characters_count()
        return (correct_chars / self.total_typed_count) * 100.0

    def get_char_status(self, index: int) -> str:
        """
        Returns 'correct', 'incorrect', or 'untyped' status for a target text letter index.
        Used by UI layers to highlight typist input correctness.
        """
        if index < 0 or index >= len(self.target_text):
            return "untyped"
            
        if index >= len(self.typed_text):
            return "untyped"
            
        if self.typed_text[index] == self.target_text[index]:
            return "correct"
        return "incorrect"

    def get_target_chars_statuses(self) -> list[str]:
        """
        Returns a list of status strings ('correct', 'incorrect', 'untyped')
        corresponding to all target_text indices.
        """
        statuses = []
        typed_len = len(self.typed_text)
        for i in range(len(self.target_text)):
            if i >= typed_len:
                statuses.append("untyped")
            elif self.typed_text[i] == self.target_text[i]:
                statuses.append("correct")
            else:
                statuses.append("incorrect")
        return statuses

