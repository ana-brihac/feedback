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


def categorize_text(text, keywords_db=None):
    """Categorize a single feedback text using keyword matching.

    Args:
        text: Raw feedback text string.
        keywords_db: Optional preloaded keywords dict.

    Returns:
        list: Categories matched (e.g., ['profesor', 'pozitiv']).
    """
    # If no text or empty text, return empty list
    if not text or not text.strip():
        return []

    # Load keywords if not provided
    if keywords_db is None:
        keywords_db = load_keywords()

    # Normalize the text: lowercase and remove diacritics
    clean_text = remove_diacritics(text.lower())

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

    return matched_categories


def categorize_all_texts(texts, keywords_db=None):
    """Categorize a list of feedback texts.

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
        # Categorize this text
        categories = categorize_text(text, keywords_db)

        if categories:
            # Text was categorized - save its categories
            categorized[text] = categories
            # Update stats counters
            for cat in categories:
                stats[cat] += 1
        else:
            # No categories found - text is uncategorized
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
