#!/usr/bin/env python3


"""Text categorizer module for feedback analysis.

Categorizes feedback text into predefined categories using
keyword matching. Falls back to LLM for uncategorized texts.

Categories: profesor, asistent, curs, laborator, teme,
            examen, materiale, pozitiv, negativ
"""

import json
import os
import unicodedata


DB_PATH = os.path.join(os.path.dirname(__file__), "keywords_db.json")

# All 9 categories used in our feedback system
CATEGORIES = [
    "profesor", "asistent", "curs", "laborator", "teme",
    "examen", "materiale", "pozitiv", "negativ"
]


def load_keywords():
    """Load keywords database from JSON file.

    Opens keywords_db.json and returns the dictionary inside.
    If the file doesn't exist, returns an empty dict with all 9 categories.
    """
    # Try to open the JSON file and load the keywords
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # If the file doesn't exist, create an empty dict with all categories
    empty_db = {cat: [] for cat in CATEGORIES}
    return empty_db


def save_keywords(db):
    """Save updated keywords database to JSON file.

    Writes the dictionary to keywords_db.json with nice formatting.
    """
    # Write the dict to the JSON file with indentation for readability
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


def remove_diacritics(text):
    """Remove Romanian diacritics from text for matching.

    Uses NFD normalization to decompose characters, then removes
    the combining marks (category Mn = Mark, nonspacing).
    Example: 'profesoară' -> 'profesoara'
    """
    # Decompose characters into base + combining marks
    normalized = unicodedata.normalize("NFD", text)
    # Keep only characters that are NOT nonspacing marks
    result = ""
    for char in normalized:
        if unicodedata.category(char) != "Mn":
            result += char
    return result


def _contains_negation(clean_text):
    """Check if text contains the Romanian negation word 'nu'.

    Uses word-boundary checking so we don't false-match words
    that merely contain 'nu' (e.g., 'numar', 'anunt', 'minunat').

    Args:
        clean_text: Lowercased, diacritics-removed text.

    Returns:
        bool: True if 'nu' appears as a standalone word.
    """
    words = clean_text.split()
    return "nu" in words


def categorize_text(text, keywords_db=None):
    """Categorize a single feedback text using keyword matching.

    Includes two safeguards before trusting local results:
      1. Negation detection  – if 'nu' appears as a standalone word,
         skip local categorization entirely (return empty list) so the
         text is forwarded to the LLM for contextual analysis.
      2. Conflict detection  – if the local scan finds BOTH 'pozitiv'
         and 'negativ', drop the sentiment categories (keep topic
         categories like profesor, curs, etc.) so the LLM can
         arbitrate the sentiment.

    Args:
        text: Raw feedback text string.
        keywords_db: Optional preloaded keywords dict.

    Returns:
        list: Categories matched (e.g., ['profesor', 'pozitiv']).
              Returns empty list when negation is detected or when
              only conflicting sentiment categories were found.
    """
    # If no text or empty text, return empty list
    if not text or not text.strip():
        return []

    # Load keywords if not provided
    if keywords_db is None:
        keywords_db = load_keywords()

    # Normalize the text: lowercase and remove diacritics
    clean_text = remove_diacritics(text.lower())

    # --- Safeguard 1: Negation detection ---
    # If the word 'nu' is present, local keyword matching is unreliable
    # because it can't understand context (e.g., 'nu preda bine').
    # Force the text to be uncategorized so the LLM handles it.
    if _contains_negation(clean_text):
        return []

    # Check each category for keyword matches
    matched_categories = []
    for category, keywords in keywords_db.items():
        for keyword in keywords:
            # Also normalize the keyword for fair comparison
            clean_keyword = remove_diacritics(keyword.lower())
            # Check if the keyword appears in the text
            if clean_keyword in clean_text:
                matched_categories.append(category)
                break  # One match per category is enough

    # --- Safeguard 2: Conflict detection ---
    # If both 'pozitiv' and 'negativ' were matched, the local algorithm
    # can't decide the true sentiment.  Drop only the sentiment categories
    # and keep any topic categories (profesor, curs, etc.) that are still
    # useful.  If no topic categories remain, the text becomes uncategorized.
    has_pozitiv = "pozitiv" in matched_categories
    has_negativ = "negativ" in matched_categories

    if has_pozitiv and has_negativ:
        matched_categories = [
            cat for cat in matched_categories
            if cat not in ("pozitiv", "negativ")
        ]

    return matched_categories


def categorize_all_texts(texts, keywords_db=None):
    """Categorize a list of feedback texts.

    Texts that are not categorized locally (empty category list) are
    added to the 'uncategorized' list for LLM fallback processing.
    This includes texts skipped due to negation or sentiment conflict.

    Args:
        texts: List of feedback text strings.
        keywords_db: Optional preloaded keywords dict.

    Returns:
        dict: {
            'categorized': {text: [categories]},
            'uncategorized': [texts_without_match],
            'stats': {category: count}
        }
    """
    # Load keywords once to avoid reloading for each text
    if keywords_db is None:
        keywords_db = load_keywords()

    categorized = {}
    uncategorized = []
    # Initialize stats with 0 for each category
    stats = {cat: 0 for cat in keywords_db.keys()}

    for text in texts:
        # Categorize this text (negation/conflict checks happen inside)
        categories = categorize_text(text, keywords_db)

        if categories:
            # Text was categorized - save its categories
            categorized[text] = categories
            # Update stats counters
            for cat in categories:
                stats[cat] += 1
        else:
            # No categories found (or negation/conflict detected)
            # Text goes to uncategorized list for LLM fallback
            uncategorized.append(text)

    return {
        "categorized": categorized,
        "uncategorized": uncategorized,
        "stats": stats
    }


def update_keywords(new_keywords):
    """Merge new keywords (from Gemini) into keywords database.

    Args:
        new_keywords: dict {category: [new_words]}
    """
    # Load the current database
    db = load_keywords()

    # Go through each category and add new words
    for category, words in new_keywords.items():
        # Make sure the category exists in the DB
        if category not in db:
            db[category] = []

        for word in words:
            # Only add the word if it's not already in the list
            if word.lower() not in db[category]:
                db[category].append(word.lower())

    # Save the updated database back to the file
    save_keywords(db)
