"""
Smart Adaptive Practice Engine for TypeMaster.
Analyzes user key error statistics and generates custom targeted practice texts
supporting English, Uzbek, and Russian dictionary wordlists.
"""
import random
import logging
from engine.text_loader import load_words_for_language
from database.repositories.key_stats_repository import KeyStatsRepository

logger = logging.getLogger("engine.adaptive_engine")

# Diagnostic default key sets for new users with no error data yet
DEFAULT_DIAGNOSTIC_KEYS = {
    "english": ['e', 't', 'a', 'o', 'i', 'n', 's', 'r', 'h', 'l'],
    "uzbek": ['a', 'o', 'i', 'e', 'u', 'r', 't', 'n', 's', 'l'],
    "russian": ['о', 'е', 'а', 'и', 'н', 'т', 'с', 'р', 'в', 'л']
}

def get_user_weak_keys(user_id: int = None, limit: int = 15, language: str = "english") -> list[str]:
    """
    Retrieves top error keys for the user from KeyStatsRepository.
    Returns up to 15 character keys sorted by error count.
    Falls back to a default diagnostic set if no user data exists.
    """
    if user_id:
        try:
            repo = KeyStatsRepository()
            rows = repo.get_top_error_keys(user_id, limit=limit)
            if rows:
                keys = [r["char_key"].lower() for r in rows if r.get("char_key")]
                if len(keys) >= 2:
                    return keys
        except Exception as err:
            logger.error(f"Error fetching weak keys for user {user_id}: {err}")

    lang_key = (language or "english").strip().lower()
    return DEFAULT_DIAGNOSTIC_KEYS.get(lang_key, DEFAULT_DIAGNOSTIC_KEYS["english"])

def generate_adaptive_text(user_id: int = None, language: str = "English", target_words_count: int = 150) -> tuple[str, list[str]]:
    """
    Generates a custom adaptive practice text tailored to the user's top weak keys.
    Supports English, Uzbek, and Russian.
    Returns a tuple of (generated_text, weak_keys_list).
    """
    lang_clean = language.strip().lower()
    if lang_clean not in ("english", "uzbek", "russian"):
        lang_clean = "english"
        
    weak_keys = get_user_weak_keys(user_id, limit=15, language=lang_clean)
    all_words = load_words_for_language(lang_clean)

    if not all_words:
        all_words = ["test", "practice", "keyboard", "master", "typing"]

    # Score words based on weak key density
    # Top 5 weak keys receive double weight for hyper-focused training
    primary_keys = set(weak_keys[:5])
    secondary_keys = set(weak_keys[5:])

    scored_words = []
    for word in all_words:
        w_lower = word.lower()
        score = 0
        for char in w_lower:
            if char in primary_keys:
                score += 2
            elif char in secondary_keys:
                score += 1
        if score > 0:
            scored_words.append((score, word))

    # Sort dictionary words by weak key density descending
    scored_words.sort(key=lambda x: x[0], reverse=True)

    # Select pool of top candidate words
    candidate_words = [w for s, w in scored_words[:80]] if scored_words else all_words[:40]

    # Generate synthetic micro-drill patterns for the top 5 weak keys (e.g. kerr erkk 5e 5r)
    top_keys = weak_keys[:5]
    micro_drills = []
    if len(top_keys) >= 2:
        for i in range(len(top_keys) - 1):
            k1, k2 = top_keys[i], top_keys[i+1]
            micro_drills.extend([
                f"{k1}{k2}{k1}{k2}",
                f"{k2}{k1}{k2}{k1}",
                f"{k1}{k1}{k2}{k2}",
                f"{k1}{k2}{k2}{k1}"
            ])

    # Combine candidate words and micro-drills to build targeted 150-word text
    assembled_words = []
    while len(assembled_words) < target_words_count:
        if candidate_words:
            assembled_words.append(random.choice(candidate_words))
        else:
            assembled_words.append(random.choice(all_words))

        # Interleave a micro-drill pattern every 4-5 words
        if micro_drills and len(assembled_words) % 5 == 0 and len(assembled_words) < target_words_count:
            assembled_words.append(random.choice(micro_drills))

    final_text = " ".join(assembled_words[:target_words_count])
    return final_text, weak_keys
