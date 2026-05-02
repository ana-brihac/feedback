#!/usr/bin/env python3


"""LLM client module for feedback text analysis.

Uses Google Gemini API as fallback for texts that cannot be
categorized by the local keyword-based algorithm.

Requires:
    - google-genai package (pip install google-genai)
    - python-dotenv package (pip install python-dotenv)
    - GEMINI_API_KEY in .env file
"""

# import os
# import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def analyze_with_gemini(texts, course_name="necunoscut"):
    """Send uncategorized texts to Gemini for batch analysis.

    Args:
        texts: List of uncategorized feedback strings.
        course_name: Course name for context in the prompt.

    Returns:
        dict: {
            'results': {text: [categories]},
            'new_keywords': {category: [suggested_words]}
        }
        or None if API key missing or error occurs.

    Expected Gemini response format:
        {
            "results": [
                {"text": "...", "categories": ["profesor", "pozitiv"]},
                ...
            ],
            "new_keywords": {
                "profesor": ["predare", "explicatie"],
                ...
            }
        }

    TODO: Build prompt with the 9 categories and the received texts,
          send batch to gemini-2.5-flash,
          parse the JSON response,
          return results + new_keywords.
    Error handling:
          - No API key -> return None
          - Gemini error -> return None, texts remain uncategorized
    """
    pass
