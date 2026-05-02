#!/usr/bin/env python3


"""Text categorizer module for feedback analysis.

Categorizes feedback text into predefined categories using
keyword matching. Falls back to LLM for uncategorized texts.

Categories: profesor, asistent, curs, laborator, teme,
            examen, materiale, pozitiv, negativ

TODO: Populate keywords_db.json with the full list of keywords.
"""

# import json
import os
# import unicodedata


DB_PATH = os.path.join(os.path.dirname(__file__), "keywords_db.json")


def load_keywords():
    """Load keywords database from JSON file.

    TODO: Load and return the dictionary from keywords_db.json.
    If the file does not exist, return an empty dict with all 9 categories.
    """
    pass


def save_keywords(db):
    """Save updated keywords database to JSON file.

    TODO: Save the updated dictionary to keywords_db.json.
    """
    pass


def remove_diacritics(text):
    """Remove Romanian diacritics from text for matching.

    TODO: NFD normalization + remove Mn (Mark, nonspacing) characters.
    Example: 'profesoară' -> 'profesoara'
    """
    pass


def categorize_text(text, keywords_db=None):
    """Categorize a single feedback text using keyword matching.

    Args:
        text: Raw feedback text string.
        keywords_db: Optional preloaded keywords dict.

    Returns:
        list: Categories matched (e.g., ['profesor', 'pozitiv']).

    TODO: Normalize text (lowercase, remove diacritics),
          search for keyword matches in each category,
          return the list of detected categories.
    """
    pass


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

    TODO: Iterate over texts, apply categorize_text(),
          separate categorized from uncategorized,
          compute per-category statistics.
    """
    pass


def update_keywords(new_keywords):
    """Merge new keywords (from Gemini) into keywords database.

    Args:
        new_keywords: dict {category: [new_words]}

    TODO: Load current DB, add new words if they don't already exist,
          save updated DB.
    """
    pass
