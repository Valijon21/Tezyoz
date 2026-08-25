"""
Text loader engine module for TypeMaster.
Loads space-separated typing target words dictionaries from static files
or provides default in-memory lists as fallbacks.
"""
from pathlib import Path
import logging

logger = logging.getLogger("engine.text_loader")

# In-memory backups to prevent runtime crashes if asset files are deleted
DEFAULT_ENGLISH_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she"
]

DEFAULT_RUSSIAN_WORDS = [
    "и", "в", "не", "на", "я", "быть", "он", "с", "что", "а",
    "по", "это", "она", "этот", "но", "они", "мы", "о", "у", "который",
    "из", "за", "бы", "весь", "же", "от", "своеgo", "для", "сказать", "как"
]

DEFAULT_UZBEK_WORDS = [
    "va", "bu", "u", "bilan", "uchun", "ham", "bir", "ki", "shuningdek", "faqat",
    "hatto", "yana", "esa", "agar", "lekin", "ammo", "chunki", "barcha", "kabi", "yil",
    "kun", "ish", "qilmoq", "demoq", "bor", "bo'sh", "boshqa", "yangi", "o'z", "kelmoq"
]

def load_words_for_language(language: str) -> list[str]:
    """
    Loads wordlists for target languages (English, Russian, Uzbek).
    Reads static file assets/texts/{language}.txt relative to this project.
    Falls back to internal default lists if the file is missing or unreadable.
    """
    if not language or not isinstance(language, str):
        logger.warning("Invalid language parameter provided to text_loader.")
        return DEFAULT_ENGLISH_WORDS
        
    lang_key = language.strip().lower()
    
    # Resolve project assets path relative to this script directory
    # text_loader.py is inside engine/, base directory is parent/
    base_dir = Path(__file__).resolve().parent.parent
    text_file_path = base_dir / "assets" / "texts" / f"{lang_key}.txt"
    
    # Fallback lists mapping
    if lang_key == "russian":
        fallback_list = DEFAULT_RUSSIAN_WORDS
    elif lang_key == "uzbek":
        fallback_list = DEFAULT_UZBEK_WORDS
    else:
        fallback_list = DEFAULT_ENGLISH_WORDS
        
    if not text_file_path.exists():
        logger.warning(f"Text dictionary file {text_file_path} not found. Using fallback wordlist.")
        return fallback_list
        
    try:
        with open(text_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Word lists are space or newline separated
        words = [w.strip() for w in content.split() if w.strip()]
        if not words:
            logger.warning(f"Text dictionary file {text_file_path} is empty. Using fallback wordlist.")
            return fallback_list
            
        return words
    except Exception as err:
        logger.error(f"Failed to read text file {text_file_path}: {err}. Using fallback.")
        return fallback_list
