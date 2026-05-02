#!/usr/bin/env python3


"""Tests for the text categorization module.

TODO: Implement tests for:
    - categorize_text() with hardcoded texts
    - categorize_all_texts() with text lists, verify stats
    - analyze_with_gemini() on uncategorized texts (if API key available)
    - update_keywords() -- verify that keywords_db.json gets updated
    - Full flow: local -> uncategorized -> Gemini -> update -> re-test
"""

# import os
# import sys


def test_categorize_text():
    """Test single text categorization.

    TODO: Test with known texts:
        - "Profesorul explica foarte bine" -> ['profesor', 'pozitiv']
        - "Laboratorul e prost organizat" -> ['laborator', 'negativ']
        - "Examenul a fost greu" -> ['examen', 'negativ']
    """
    pass


def test_categorize_all_texts():
    """Test batch categorization and stats.

    TODO: Test with a list of texts, verify:
        - All texts are either categorized or uncategorized
        - Stats correctly reflect the count per category
    """
    pass


def test_update_keywords():
    """Test keyword database update.

    TODO: Test with new words:
        - Add new words -> verify they appear in DB
        - Add existing words -> verify no duplicates
    """
    pass


def test_analyze_with_gemini():
    """Test Gemini API integration (requires API key).

    TODO: Skip if GEMINI_API_KEY is not set.
          Send 2-3 simple texts, verify response format.
    """
    pass


if __name__ == "__main__":
    print("Running categorizer tests...")
    test_categorize_text()
    test_categorize_all_texts()
    test_update_keywords()
    test_analyze_with_gemini()
    print("All tests passed (or skipped).")
