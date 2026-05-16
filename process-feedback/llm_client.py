#!/usr/bin/env python3


"""LLM client module for feedback text analysis.

Uses Google Gemini API as fallback for texts that cannot be
categorized by the local keyword-based algorithm.

Requires:
    - google-genai package (pip install google-genai)
    - python-dotenv package (pip install python-dotenv)
    - GEMINI_API_KEY in .env file
"""

import os
import json

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
    """
    # Check if the API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment. Skipping LLM analysis.")
        return None

    # Try to import the google genai library
    try:
        from google import genai
    except ImportError:
        print("google-genai package not installed. Skipping LLM analysis.")
        return None

    # If there are no texts to analyze, return empty results
    if not texts:
        return {"results": {}, "new_keywords": {}}

    # Build the prompt for Gemini
    # Instructions in English (LLMs follow English more reliably),
    # but category names stay in Romanian since the data is Romanian
    prompt = f"""You are an assistant that analyzes student feedback for the course "{course_name}".
The feedback texts are written in Romanian.

Classify each text below into one or more of these 9 categories:
- profesor (comments about the course lecturer)
- asistent (comments about the teaching assistant)
- curs (aspects related to lectures)
- laborator (aspects related to labs/seminars)
- teme (homework/projects/deadlines)
- examen (exams/tests/grading)
- materiale (slides/documentation/resources)
- pozitiv (positive sentiment)
- negativ (negative sentiment)

Texts to analyze:
"""
    # Add each text with a number for easy reference
    for i, text in enumerate(texts):
        prompt += f'{i + 1}. "{text}"\n'

    prompt += """
Respond STRICTLY in JSON format, with no extra explanation:
{
    "results": [
        {"text": "original text here", "categories": ["profesor", "pozitiv"]}
    ],
    "new_keywords": {
        "profesor": ["new_keyword1", "new_keyword2"]
    }
}

In "new_keywords", include relevant Romanian keywords extracted from the texts
that could be useful for future automated categorization.
"""

    try:
        # Create the Gemini client and send the request
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Get the response text
        response_text = response.text

        # Clean up the response (remove markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        # Parse the JSON response from Gemini
        parsed = json.loads(response_text)

        # Convert the results list into a dict {text: [categories]}
        results_dict = {}
        for item in parsed.get("results", []):
            text = item.get("text", "")
            categories = item.get("categories", [])
            results_dict[text] = categories

        # Get the suggested new keywords
        new_keywords = parsed.get("new_keywords", {})

        return {
            "results": results_dict,
            "new_keywords": new_keywords
        }

    except Exception as e:
        # If anything goes wrong (network error, bad JSON, etc.)
        # we return None and the texts stay uncategorized
        print(f"Gemini API error: {e}")
        return None
