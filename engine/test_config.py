"""
TestConfiguration class for TypeMaster.
Validates and tracks the active language and duration constraints for a typing test session.
"""
from app.config import SUPPORTED_MODES, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

class TestConfig:
    """Holds and validates typing test setup parameters (language and duration)."""
    def __init__(self, language: str = DEFAULT_LANGUAGE, duration: int = 60):
        self.set_language(language)
        self.set_duration(duration)

    def set_language(self, language: str):
        """Validates and sets the language choice (allows bypassing for custom files)."""
        if not language or not isinstance(language, str):
            raise ValueError("Til nomi matn bo'lishi shart!")
            
        normalized = language.strip()
        # Bypass SUPPORTED_LANGUAGES validation if it refers to a custom uploaded file
        if not (normalized.startswith("Fayl:") or normalized.startswith("File:")):
            normalized_cap = normalized.capitalize()
            if normalized_cap not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Qo'llab-quvvatlanmaydigan til: {language}")
            normalized = normalized_cap
        self._language = normalized

    def get_language(self) -> str:
        """Returns the normalized language name."""
        return self._language

    def set_duration(self, duration: int):
        """Validates and sets the test duration in seconds."""
        try:
            val = int(duration)
        except (ValueError, TypeError):
            raise ValueError("Test vaqti son bo'lishi shart!")
            
        if val <= 0:
            raise ValueError("Test vaqti musbat son bo'lishi shart!")
        self._duration = val

    def get_duration(self) -> int:
        """Returns the test duration in seconds."""
        return self._duration

    @property
    def language(self) -> str:
        return self.get_language()

    @language.setter
    def language(self, value: str):
        self.set_language(value)

    @property
    def duration(self) -> int:
        return self.get_duration()

    @duration.setter
    def duration(self, value: int):
        self.set_duration(value)
