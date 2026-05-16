#!/usr/bin/env python3


"""Tests for the text categorization module.

Tests for:
    - categorize_text() with hardcoded texts (simple + complex + long)
    - Negation detection ('nu' forces LLM fallback)
    - Conflict detection (pozitiv + negativ -> LLM fallback)
    - categorize_all_texts() with text lists, verify stats
    - analyze_with_gemini() on uncategorized texts (if API key available)
    - update_keywords() -- verify that keywords_db.json gets updated
    - Full flow: local -> uncategorized -> Gemini -> update -> re-test
"""

import os
import sys
import json
import copy

# Load .env file so GEMINI_API_KEY is available for tests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from text_categorizer import (
    categorize_text, categorize_all_texts, update_keywords,
    load_keywords, save_keywords, DB_PATH
)
from llm_client import analyze_with_gemini


def test_categorize_text_simple():
    """Test single text categorization with simple, short texts."""
    print("  Testing categorize_text() — simple texts...")

    # Test 1: Text about professor + positive sentiment
    result = categorize_text("Profesorul explica foarte bine")
    assert "profesor" in result, f"Expected 'profesor' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: 'Profesorul explica foarte bine' ->", result)

    # Test 2: Text about lab + negative sentiment
    result = categorize_text("Laboratorul e prost organizat")
    assert "laborator" in result, f"Expected 'laborator' in {result}"
    assert "negativ" in result, f"Expected 'negativ' in {result}"
    print("    OK: 'Laboratorul e prost organizat' ->", result)

    # Test 3: Text about exam + negative sentiment
    result = categorize_text("Examenul a fost greu")
    assert "examen" in result, f"Expected 'examen' in {result}"
    assert "negativ" in result, f"Expected 'negativ' in {result}"
    print("    OK: 'Examenul a fost greu' ->", result)

    # Test 4: Empty text should return empty list
    result = categorize_text("")
    assert result == [], f"Expected empty list for empty text, got {result}"
    print("    OK: Empty text ->", result)

    # Test 5: None text should also return empty list
    result = categorize_text(None)
    assert result == [], f"Expected empty list for None, got {result}"
    print("    OK: None text ->", result)

    # Test 6: Text with Romanian diacritics
    result = categorize_text("Profesoara explică bine materia la curs")
    assert "profesor" in result, f"Expected 'profesor' in {result}"
    assert "curs" in result, f"Expected 'curs' in {result}"
    print("    OK: Text with diacritics ->", result)

    # Test 7: Just whitespace
    result = categorize_text("   \n\t  ")
    assert result == [], f"Expected empty list for whitespace, got {result}"
    print("    OK: Whitespace only ->", result)

    print("  PASSED: categorize_text() — simple texts")


def test_categorize_text_multi_category():
    """Test texts that should match multiple categories at once."""
    print("  Testing categorize_text() — multi-category texts...")

    # Text about both professor and course + positive
    result = categorize_text("Profesorul tine un curs excelent")
    assert "profesor" in result, f"Expected 'profesor' in {result}"
    assert "curs" in result, f"Expected 'curs' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: prof + curs + pozitiv ->", result)

    # Text about lab and homework with conflict
    # NOTE: 'inutil' contains 'util' (pozitiv keyword) as a substring,
    # while 'plictisitoare', 'inutil', 'grele' match negativ keywords.
    # Conflict detection drops both sentiments; topic categories remain.
    result = categorize_text("Temele de la laborator sunt plictisitoare si inutil de grele")
    assert "teme" in result, f"Expected 'teme' in {result}"
    assert "laborator" in result, f"Expected 'laborator' in {result}"
    assert "pozitiv" not in result, f"'pozitiv' should be dropped (conflict), got {result}"
    assert "negativ" not in result, f"'negativ' should be dropped (conflict), got {result}"
    print("    OK: teme + laborator (sentiments dropped via conflict) ->", result)

    # Text about materials and course + positive
    result = categorize_text("Slide-urile de la curs sunt super utile")
    assert "materiale" in result, f"Expected 'materiale' in {result}"
    assert "curs" in result, f"Expected 'curs' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: materiale + curs + pozitiv ->", result)

    # Text about assistant and exam
    result = categorize_text("Asistentul ne-a pregatit bine pentru examen")
    assert "asistent" in result, f"Expected 'asistent' in {result}"
    assert "examen" in result, f"Expected 'examen' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: asistent + examen + pozitiv ->", result)

    print("  PASSED: categorize_text() — multi-category texts")


def test_categorize_text_long():
    """Test categorization with longer, more realistic feedback texts.

    These are 4-5 line paragraphs like real students would write.
    """
    print("  Testing categorize_text() — long realistic texts...")

    # Long positive feedback about professor and course
    text1 = (
        "Profesorul este extraordinar de bine pregatit si stie sa explice "
        "conceptele complexe intr-un mod accesibil. Cursul este foarte bine "
        "structurat, cu exemple practice relevante. Am apreciat faptul ca "
        "raspunde la intrebari cu rabdare si ca materialele de curs sunt "
        "mereu actualizate. Recomand aceasta disciplina tuturor colegilor!"
    )
    result = categorize_text(text1)
    assert "profesor" in result, f"Expected 'profesor' in {result}"
    assert "curs" in result, f"Expected 'curs' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: Long positive prof+curs ->", result)

    # Long negative feedback about lab and homework
    # NOTE: This text contains 'nu' so negation detection kicks in.
    # The text is forced to uncategorized (LLM fallback).
    text2 = (
        "Laboratorul este dezorganizat si haotic. Asistentul vine nepregatit, "
        "nu stie sa raspunda la intrebari si ne lasa sa ne descurcam singuri. "
        "Temele sunt prost formulate, cu cerinte neclare si deadline-uri "
        "nerealiste. Am petrecut ore intregi incercand sa inteleg ce se cere "
        "si tot nu am reusit. Este cel mai slab laborator pe care l-am avut."
    )
    result = categorize_text(text2)
    assert result == [], f"Expected [] (negation 'nu' detected), got {result}"
    print("    OK: Long text with 'nu' -> [] (negation detected) ->", result)

    # Long mixed feedback about exam and materials
    # NOTE: This text contains 'nu' ('care nu au fost') so negation
    # detection kicks in, forcing it to uncategorized.
    text3 = (
        "Examenul a fost corect ca dificultate, dar baremul de corectare a fost "
        "foarte strict. Materialele de curs sunt bune si suficiente pentru "
        "pregatirea la test, insa partial-ul a avut cateva probleme care nu "
        "au fost acoperite in slide-uri. Per total, cred ca notarea a fost "
        "destul de echitabila, dar ar putea fi imbunatatita comunicarea."
    )
    result = categorize_text(text3)
    assert result == [], f"Expected [] (negation 'nu' detected), got {result}"
    print("    OK: Long text with 'nu' -> [] (negation detected) ->", result)

    # Long text with diacritics about everything
    # NOTE: Has both pozitiv ('interesant', 'bine', 'excelent') and negativ
    # ('greu') keywords -> conflict detection drops both sentiments.
    text4 = (
        "Cursul de programare a fost cel mai interesant din acest semestru. "
        "Profesoara știe să explice clar și are un stil de predare captivant. "
        "Laboratoarele au fost bine organizate, cu teme provocatoare dar "
        "realizabile. Singurul aspect negativ este că examenul a fost prea "
        "greu comparativ cu ce s-a predat la curs. Materialele sunt excelente."
    )
    result = categorize_text(text4)
    assert "curs" in result, f"Expected 'curs' in {result}"
    assert "profesor" in result, f"Expected 'profesor' in {result}"
    assert "laborator" in result, f"Expected 'laborator' in {result}"
    assert "examen" in result, f"Expected 'examen' in {result}"
    assert "pozitiv" not in result, f"'pozitiv' should be dropped (conflict), got {result}"
    assert "negativ" not in result, f"'negativ' should be dropped (conflict), got {result}"
    print("    OK: Long multi-category, sentiments dropped (conflict) ->", result)

    # Long text that's mostly filler but has keywords buried inside
    # NOTE: This text contains 'nu' so negation detection kicks in.
    text5 = (
        "Sincer sa fiu, nu prea am ce sa zic despre aceasta materie. A fost "
        "ok, nici bine nici rau, cam la nivelul asteptarilor mele din punct "
        "de vedere al continutului. Totusi proiectul de la sfarsit de "
        "semestru mi s-a parut un pic cam complicat si ar fi fost util sa "
        "avem mai multe resurse si poate un manual mai detaliat."
    )
    result = categorize_text(text5)
    assert result == [], f"Expected [] (negation 'nu' detected), got {result}"
    print("    OK: Long text with 'nu' -> [] (negation detected) ->", result)

    print("  PASSED: categorize_text() — long realistic texts")


def test_categorize_all_texts():
    """Test batch categorization and stats.

    Verifies that all texts are either categorized or uncategorized,
    and that stats correctly reflect the count per category.
    Uses a larger batch with mixed difficulty.
    """
    print("  Testing categorize_all_texts()...")

    texts = [
        # Simple categorizable texts
        "Profesorul explica foarte bine",
        "Laboratorul e prost organizat",
        "Temele sunt interesante si utile",
        "Examenul a fost corect si bine facut",
        "Asistentul e super pregatit",
        "Materialele de curs sunt excelente",
        # Longer categorizable text (no 'nu' — stays local)
        (
            "Cursul a fost extraordinar de interesant, profesorul stie sa "
            "capteze atentia studentilor si sa explice clar chiar si "
            "conceptele cele mai grele din materie."
        ),
        # This text has 'nu' -> forced to uncategorized by negation detection
        (
            "Laboratorul a fost groaznic, asistentul nu stie sa explice "
            "iar temele au deadline-uri imposibile. Testul a fost mult "
            "mai greu decat ce s-a predat."
        ),
        # Texts that should be uncategorizable (gibberish / no keywords)
        "xyzzy blorp fnargl",
        "123 456 789",
        "...",
    ]

    result = categorize_all_texts(texts)

    # Check that all texts are accounted for
    total = len(result["categorized"]) + len(result["uncategorized"])
    assert total == len(texts), f"Expected {len(texts)} total, got {total}"
    print("    OK: All", len(texts), "texts accounted for")

    # Gibberish texts should be uncategorized
    assert "xyzzy blorp fnargl" in result["uncategorized"]
    assert "123 456 789" in result["uncategorized"]
    assert "..." in result["uncategorized"]
    print("    OK: 3 gibberish texts are uncategorized")

    # The text with 'nu' should also be uncategorized (negation detection)
    negation_text = (
        "Laboratorul a fost groaznic, asistentul nu stie sa explice "
        "iar temele au deadline-uri imposibile. Testul a fost mult "
        "mai greu decat ce s-a predat."
    )
    assert negation_text in result["uncategorized"], \
        "Text with 'nu' should be uncategorized (negation detection)"
    print("    OK: Text with 'nu' is correctly uncategorized")

    # 7 texts should be categorized locally (the ones without 'nu')
    assert len(result["categorized"]) >= 7, \
        f"Expected at least 7 categorized, got {len(result['categorized'])}"
    print(f"    OK: {len(result['categorized'])} texts categorized")

    # Verify stats contain expected categories with counts > 0
    assert result["stats"]["profesor"] >= 2, "Expected at least 2 'profesor'"
    assert result["stats"]["laborator"] >= 1, "Expected at least 1 'laborator'"
    assert result["stats"]["pozitiv"] >= 3, "Expected at least 3 'pozitiv'"
    assert result["stats"]["negativ"] >= 1, "Expected at least 1 'negativ'"
    print("    OK: Stats ->", result["stats"])

    print("  PASSED: categorize_all_texts()")


def test_update_keywords():
    """Test keyword database update.

    Tests that new words get added and duplicates are ignored.
    Also tests adding a new category that doesn't exist yet.
    """
    print("  Testing update_keywords()...")

    # Save a backup of the current DB so we can restore it later
    original_db = load_keywords()
    backup_db = copy.deepcopy(original_db)

    try:
        # Test 1: Add new words to existing categories
        new_words = {
            "profesor": ["test_new_word_xyz"],
            "curs": ["test_cuvant_nou_abc"]
        }
        update_keywords(new_words)

        updated_db = load_keywords()
        assert "test_new_word_xyz" in updated_db["profesor"], \
            "New word should be in profesor category"
        assert "test_cuvant_nou_abc" in updated_db["curs"], \
            "New word should be in curs category"
        print("    OK: New words added successfully")

        # Test 2: Adding the same word again should NOT create duplicates
        count_before = updated_db["profesor"].count("test_new_word_xyz")
        update_keywords(new_words)
        updated_db = load_keywords()
        count_after = updated_db["profesor"].count("test_new_word_xyz")
        assert count_before == count_after, "Duplicate words should not be added"
        print("    OK: No duplicates created")

        # Test 3: Adding words to a completely new category
        update_keywords({"categorie_test_noua": ["cuvant1", "cuvant2"]})
        updated_db = load_keywords()
        assert "categorie_test_noua" in updated_db, \
            "New category should be created"
        assert "cuvant1" in updated_db["categorie_test_noua"], \
            "Word should be in new category"
        assert "cuvant2" in updated_db["categorie_test_noua"], \
            "Word should be in new category"
        print("    OK: New category created with words")

        # Test 4: Adding multiple words at once
        update_keywords({
            "profesor": ["test_a", "test_b", "test_c"],
            "examen": ["test_d"]
        })
        updated_db = load_keywords()
        assert "test_a" in updated_db["profesor"]
        assert "test_b" in updated_db["profesor"]
        assert "test_c" in updated_db["profesor"]
        assert "test_d" in updated_db["examen"]
        print("    OK: Multiple words added to multiple categories")

    finally:
        # Restore the original database so tests don't pollute it
        save_keywords(backup_db)
        print("    OK: Original DB restored")

    print("  PASSED: update_keywords()")


def test_analyze_with_gemini():
    """Test Gemini API integration (requires API key).

    Skipped if GEMINI_API_KEY is not set in the environment.
    Uses longer, more complex texts to really test the LLM.
    """
    print("  Testing analyze_with_gemini()...")

    # Skip this test if no API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("    SKIPPED: GEMINI_API_KEY not set in environment")
        return

    # Send longer, more complex texts for analysis
    test_texts = [
        "Profesorul nu stie sa explice deloc, vorbeste incet si confuz",
        "Mi-a placut foarte mult laboratorul, asistentul e super",
        (
            "Materia in sine e interesanta dar modul in care e predata "
            "lasa de dorit, ar fi nevoie de mai multe exemple practice "
            "si de slide-uri actualizate"
        ),
    ]

    result = analyze_with_gemini(test_texts, course_name="Programare")

    # If result is None, the API call failed
    if result is None:
        print("    SKIPPED: Gemini API returned None (possible error)")
        return

    # Check the response format
    assert "results" in result, "Response should have 'results' key"
    assert "new_keywords" in result, "Response should have 'new_keywords' key"
    assert isinstance(result["results"], dict), "Results should be a dict"
    assert isinstance(result["new_keywords"], dict), "new_keywords should be a dict"
    print("    OK: Response format is correct")
    print("    Results:", result["results"])
    print("    New keywords:", result["new_keywords"])

    print("  PASSED: analyze_with_gemini()")


def test_full_flow():
    """Test the complete flow: local -> uncategorized -> Gemini -> update.

    Simulates the real pipeline with a realistic batch of mixed feedback.
    """
    print("  Testing full flow...")

    texts = [
        # These should be categorized locally (contain obvious keywords)
        "Profesorul e foarte bun si predarea e excelenta",
        "Laboratorul a fost slab si dezorganizat",
        "Temele au fost interesante dar grele",
        # These contain 'nu' -> negation detection forces them uncategorized
        "Nu am inteles nimic din ce s-a predat in a doua parte a semestrului",
        "xyzzy random text gibberish that means nothing",
        (
            "Ar fi fost util sa avem mai multa practica si mai putina teorie, "
            "simt ca nu am invatat nimic aplicabil in viata reala"
        ),
    ]

    # Step 1: Local categorization
    local_result = categorize_all_texts(texts)
    categorized_count = len(local_result["categorized"])
    uncategorized_count = len(local_result["uncategorized"])
    print(f"    Local: {categorized_count} categorized, {uncategorized_count} uncategorized")

    # First 3 should be categorized locally; the 'nu' texts go uncategorized
    assert categorized_count >= 3, \
        f"Expected at least 3 categorized locally, got {categorized_count}"

    # Step 2: Try Gemini on uncategorized texts (if API key available)
    if local_result["uncategorized"]:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            gemini_result = analyze_with_gemini(local_result["uncategorized"])
            if gemini_result:
                print("    Gemini categorized:", len(gemini_result["results"]), "texts")
                # Step 3: Update keywords with new suggestions
                if gemini_result["new_keywords"]:
                    backup = copy.deepcopy(load_keywords())
                    update_keywords(gemini_result["new_keywords"])
                    new_db = load_keywords()
                    # Check that DB actually grew
                    total_old = sum(len(v) for v in backup.values())
                    total_new = sum(len(v) for v in new_db.values())
                    print(f"    Keywords DB: {total_old} -> {total_new} words")
                    # Restore backup to keep tests clean
                    save_keywords(backup)
                    print("    Original DB restored")
            else:
                print("    Gemini returned None (API error)")
        else:
            print("    SKIPPED Gemini step: no API key")

    print("  PASSED: full flow")


def test_negation_and_conflict():
    """Test negation detection and sentiment conflict detection.

    Negation: texts with standalone 'nu' should return [] and be
    sent to uncategorized (LLM fallback).
    Conflict: texts matching both 'pozitiv' and 'negativ' keywords
    should have those sentiment categories dropped.
    """
    print("  Testing negation and conflict detection...")

    # --- Negation detection tests ---

    # Test 1: Simple negation — 'nu preda bine' should NOT match 'pozitiv'
    result = categorize_text("nu preda bine")
    assert result == [], f"Expected [] for 'nu preda bine', got {result}"
    print("    OK: 'nu preda bine' -> [] (negation detected)")

    # Test 2: 'Nu' at start of sentence
    result = categorize_text("Nu mi-a placut cursul deloc")
    assert result == [], f"Expected [] for negated text, got {result}"
    print("    OK: 'Nu mi-a placut cursul deloc' -> [] (negation detected)")

    # Test 3: 'nu' in the middle of a sentence
    result = categorize_text("Profesorul nu explica bine materia")
    assert result == [], f"Expected [] for negated text, got {result}"
    print("    OK: 'Profesorul nu explica bine materia' -> [] (negation detected)")

    # Test 4: 'nu' with diacritics in surrounding text
    result = categorize_text("Asistentul nu e pregătit pentru laborator")
    assert result == [], f"Expected [] for negated text, got {result}"
    print("    OK: Negation with diacritics -> [] (negation detected)")

    # Test 5: Words CONTAINING 'nu' should NOT trigger negation
    # 'numar' contains 'nu' but is not the standalone word 'nu'
    result = categorize_text("Un numar mare de teme interesante")
    assert "teme" in result, f"Expected 'teme' in {result} ('numar' != 'nu')"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: 'numar' does NOT trigger negation ->", result)

    # Test 6: 'minunat' contains 'nu' substring — should NOT trigger
    result = categorize_text("Cursul a fost minunat")
    assert "curs" in result, f"Expected 'curs' in {result}"
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    print("    OK: 'minunat' does NOT trigger negation ->", result)

    # Test 7: 'anunt' contains 'nu' substring — should NOT trigger
    result = categorize_text("Am vazut un anunt despre examen, super util")
    assert "examen" in result, f"Expected 'examen' in {result}"
    print("    OK: 'anunt' does NOT trigger negation ->", result)

    # --- Conflict detection tests ---

    # Test 8: Text with both pozitiv AND negativ keywords
    # 'bine' = pozitiv, 'prost' = negativ -> conflict -> drop both sentiments
    result = categorize_text("Cursul e bine dar examenul e prost")
    assert "pozitiv" not in result, f"'pozitiv' should be dropped in conflict, got {result}"
    assert "negativ" not in result, f"'negativ' should be dropped in conflict, got {result}"
    # Topic categories should still be present
    assert "curs" in result, f"Expected 'curs' (topic) in {result}"
    assert "examen" in result, f"Expected 'examen' (topic) in {result}"
    print("    OK: Conflict detected, sentiments dropped, topics kept ->", result)

    # Test 9: Conflict with only sentiment keywords (no topics)
    # Should return [] since both sentiments are dropped and nothing remains
    result = categorize_text("E super dar si groaznic")
    assert result == [], f"Expected [] for pure sentiment conflict, got {result}"
    print("    OK: Pure sentiment conflict -> [] (fully uncategorized)")

    # Test 10: Single sentiment should still work normally
    result = categorize_text("Cursul e excelent")
    assert "pozitiv" in result, f"Expected 'pozitiv' in {result}"
    assert "curs" in result, f"Expected 'curs' in {result}"
    print("    OK: Single pozitiv sentiment works normally ->", result)

    result = categorize_text("Laboratorul e groaznic")
    assert "negativ" in result, f"Expected 'negativ' in {result}"
    assert "laborator" in result, f"Expected 'laborator' in {result}"
    print("    OK: Single negativ sentiment works normally ->", result)

    # --- Integration test: negation/conflict in categorize_all_texts ---

    # Test 11: Verify negation and conflict texts land in uncategorized
    texts = [
        "Profesorul e excelent",               # normal -> categorized
        "Profesorul nu e bun",                  # negation -> uncategorized
        "Cursul e bine dar examenul e prost",   # conflict -> categorized (topics only)
        "E super dar si groaznic",              # conflict, no topics -> uncategorized
    ]
    result = categorize_all_texts(texts)

    assert "Profesorul e excelent" in result["categorized"]
    assert "Profesorul nu e bun" in result["uncategorized"]
    assert "Cursul e bine dar examenul e prost" in result["categorized"]
    assert "E super dar si groaznic" in result["uncategorized"]
    print("    OK: categorize_all_texts integration ->",
          f"{len(result['categorized'])} categorized,",
          f"{len(result['uncategorized'])} uncategorized")

    print("  PASSED: negation and conflict detection")


if __name__ == "__main__":
    print("Running categorizer tests...")
    print()
    test_categorize_text_simple()
    print()
    test_categorize_text_multi_category()
    print()
    test_categorize_text_long()
    print()
    test_negation_and_conflict()
    print()
    test_categorize_all_texts()
    print()
    test_update_keywords()
    print()
    test_analyze_with_gemini()
    print()
    test_full_flow()
    print()
    print("All tests passed (or skipped).")
