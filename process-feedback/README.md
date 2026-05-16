# Process curs.pub.ro Feedback

These are are a set of quick'n'dirty scripts to process [curs.pub.ro](http://curs.pub.ro) feedback. curs.pub.ro is based on [Moodle](https://moodle.org) and is used in [University POLITEHNICA of Bucharest](http://www.upb.ro).

## Requirements

You need the `gnumeric` package installed on your system. It's easy to install it on Linux systems. You can use brew or MacPorts on macOS.


Make sure `gnumeric` package is installed. We need the `ssconvert` tool

```
razvan@drone:~/feedback.git$ which ssconvert
/usr/bin/ssconvert
razvan@drone:~/feedback.git$ dpkg -S $(which ssconvert)
gnumeric: /usr/bin/ssconvert
```

## Setting Up

Clone the repository.

```
razvan@drone:~$ git clone https://github.com/cs-pub-ro/feedback feedback.git
Cloning into 'feedback.git'...
remote: Enumerating objects: 53, done.
remote: Total 53 (delta 0), reused 0 (delta 0), pack-reused 53
Unpacking objects: 100% (53/53), done.
```

Change to the repository folder, create the processing folder (`so2`) in our case and get the initial "unprocessed" spreadsheet in that folder.

```
razvan@drone:~$ cd feedback.git/process-feedback/
razvan@drone:~/feedback.git/process-feedback$ mkdir so2
 LICENSE   README  'SO2 2013-2014 - Feedback studenti - neprelucrat.xls'   csv2xls.sh   process_feedback.py   so2   xls2csv.sh
razvan@drone:~/feedback.git/process-feedback$ cp ~/school/so2/SO2\ 2013-2014\ -\ Feedback\ studenti\ -\ neprelucrat.xls so2/
razvan@drone:~/feedback.git/process-feedback$ ls so2
'SO2 2013-2014 - Feedback studenti - neprelucrat.xls'
```

## Repository Contents

There are three scripts as part of the repository:
  * `xls2csv.sh` converts all `.xls` files to `.csv` files in the folder passed as argument. `.csv` files are required for the actual processing.
  * `process_feedback.py` does the actual processing resulting in a new file with the `-prelucrat.csv` suffix.
  * `csv2xls.sh` converts the resulting `-prelucrat.csv` file to an `.xls` file.

See how to use them below.

## Processing the Feedback

We run scripts in order: `xls2csv.sh`, `process_feedback.py` and `csv2xls.sh`.

```
razvan@drone:~/feedback.git/process-feedback$ ./xls2csv.sh
Usage: ./xls2csv.sh DIR_DATA
razvan@drone:~/feedback.git/process-feedback$ ./xls2csv.sh so2/
Convert SO2 2013-2014 - Feedback studenti - neprelucrat.xls to SO2 2013-2014 - Feedback studenti - neprelucrat.csv
razvan@drone:~/feedback.git/process-feedback$ ls so2/
'SO2 2013-2014 - Feedback studenti - neprelucrat.csv'  'SO2 2013-2014 - Feedback studenti - neprelucrat.xls'
razvan@drone:~/feedback.git/process-feedback$ ./process_feedback.py so2/
Generate results in so2//SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.csv
razvan@drone:~/feedback.git/process-feedback$ ls so2/
'SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.csv'  'SO2 2013-2014 - Feedback studenti - neprelucrat.csv'  'SO2 2013-2014 - Feedback studenti - neprelucrat.xls'
razvan@drone:~/feedback.git/process-feedback$ cat so2/SO2\ 2013-2014\ -\ Feedback\ studenti\ -\ neprelucrat-prelucrat.csv
"categorie","count","Nr. ore","Eval gen","Nota astept","Incarcare mai mare","Prezenta C","Prezenta L","Preg. C","Preg. L","Expl clare C","Expl clare L","Rasp clare C","Rasp clare L","Interes C","Interes L","Comport. C","Comport. L","Expl supl C","Expl supl L","Materiale C","Materiale L","Nr. teme","Indepl. ob."
"Minim","51","5","3","5","0","1","2","3","4","2","3","3","4","2","3","3","33","4","3","4","2","4","2"
"Mediu","51","9.65","4.61","7.82","1.69","3.1","3.78","5.18","5.41","4.59","5.12","5.14","5.35","4.71","5.22","5.2","2345.04","5.37","5.12","5.33","4.71","5.2","4.22"
"Maxim","51","17","6","10","2","4","4","6","6","6","6","6","6","6","6","6","9953","6","6","6","6","6","6"
"Octavian Purdila","49","9.53","4.61","7.86","1.67","3.08","3.8","5.18","5.43","4.59","5.16","5.16","5.39","4.71","5.24","5.22","2221.84","5.41","5.14","5.37","4.69","5.2","4.24"
"Razvan Deaconescu","2","12.5","4.5","7.0","2.0","3.5","3.5","5.0","5.0","4.5","4.0","4.5","4.5","4.5","4.5","4.5","5363.5","4.5","4.5","4.5","5.0","5.0","3.5"
"Razvan Deaconescu","20","10.55","4.6","8.35","1.7","3.15","3.9","5.2","5.7","4.6","5.45","5.35","5.6","4.75","5.55","5.5","2846.65","5.7","5.2","5.5","4.65","5.35","4.25"
"Daniel Baluta","9","9.33","4.78","7.33","1.78","3.44","3.89","5.44","5.44","4.78","5.0","4.89","5.11","4.56","5.0","5.44","1610.0","5.33","5.33","5.33","5.22","5.22","4.22"
"Dumitru-Vlăduţ DOGARU","16","8.94","4.5","7.31","1.56","2.94","3.69","5.06","5.19","4.63","4.94","5.06","5.25","4.81","5.19","4.75","1988.75","5.13","5.0","5.19","4.94","5.25","4.31"
"Laura-Mihaela VASILESCU","6","9.0","4.67","8.17","1.83","2.83","3.5","5.0","5.0","4.17","4.67","5.0","5.17","4.5","4.5","5.0","2725.67","5.0","4.83","5.17","3.5","4.5","3.83"
razvan@drone:~/feedback.git/process-feedback$ ./csv2xls.sh
Usage: ./csv2xls.sh DIR_DATA
razvan@drone:~/feedback.git/process-feedback$ ./csv2xls.sh so2/
Convert SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.csv to SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.xls
razvan@drone:~/feedback.git/process-feedback$ ls so2/
'SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.csv'  'SO2 2013-2014 - Feedback studenti - neprelucrat.csv'
'SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.xls'  'SO2 2013-2014 - Feedback studenti - neprelucrat.xls'
```

The resulting file `SO2 2013-2014 - Feedback studenti - neprelucrat-prelucrat.xls` shows all numerical results for teachers and assistants.

## Text Categorization (WIP)

In addition to the numerical processing above, a text categorization module is being developed to automatically analyze the qualitative (free-text) feedback fields (`positive`, `negative`, `other`).

### How It Works

Feedback texts are categorized into 9 labels:

| Category | What it detects |
|----------|----------------|
| `profesor` | Comments about the course lecturer |
| `asistent` | Comments about the teaching assistant |
| `curs` | Aspects related to the course/lectures |
| `laborator` | Aspects related to labs/seminars |
| `teme` | Homework/projects/deadlines |
| `examen` | Exams/tests/grades/grading criteria |
| `materiale` | Slides/documentation/resources |
| `pozitiv` | Positive sentiment |
| `negativ` | Negative sentiment |

The system uses a **two-level approach**:

1. **Local keyword matching** (`text_categorizer.py`) — fast, zero-cost classification using a keyword database (`keywords_db.json`). Handles ~70-80% of texts.
2. **LLM fallback** (`llm_client.py`) — sends uncategorized texts to Google Gemini API for context-aware classification. Also suggests new keywords to improve future local matching.

### Negation & Conflict Detection

The local keyword matcher includes two safeguards to avoid misclassification:

**1. Negation detection** — If the Romanian negation word `nu` appears as a standalone word in the text (e.g., *"nu predă bine"*, *"nu e pregătit"*), the local categorizer skips the text entirely and sends it to the LLM for contextual analysis. This prevents false positives like matching `bine` ("well") as `pozitiv` when the student actually wrote *"nu predă bine"* ("doesn't teach well").

> Word-boundary checking is used so words that merely *contain* `nu` (e.g., `număr`, `anunț`, `minunat`) do **not** trigger this safeguard.

**2. Conflict detection** — If the local scan finds **both** `pozitiv` and `negativ` keywords in the same text, it drops both sentiment categories (since the algorithm can't determine the true sentiment) and keeps only the topic categories (`profesor`, `curs`, `laborator`, etc.). If no topic categories remain after dropping sentiments, the text becomes uncategorized and goes to the LLM.

| Scenario | Example | Behavior |
|----------|---------|----------|
| Negation | *"Profesorul nu explică bine"* | → `[]` (forced to LLM) |
| Conflict (with topics) | *"Cursul e bine dar examenul e prost"* | → `['curs', 'examen']` (sentiments dropped) |
| Conflict (no topics) | *"E super dar și groaznic"* | → `[]` (forced to LLM) |
| Normal | *"Profesorul explică foarte bine"* | → `['profesor', 'pozitiv']` (unchanged) |

### New & Modified Files

- `keywords_db.json` — keyword database per category (editable)
- `text_categorizer.py` — local keyword-based categorizer (with negation & conflict detection)
- `llm_client.py` — Gemini API client (requires `.env` with `GEMINI_API_KEY`)
- `test_categorizer.py` — tests for the categorization module (includes negation & conflict tests)
- `processor.py` — contains `TODO` comments where the new categorization logic will be integrated into the main pipeline

### Setup

To use the LLM fallback, create a `.env` file in `process-feedback/`:

```
GEMINI_API_KEY=your_api_key_here
```

Install the required packages:

```
pip install google-genai python-dotenv
```

The local keyword matching works without any extra setup.

---

## Project Summary

This project automates the processing and analysis of student feedback from [curs.pub.ro](http://curs.pub.ro) (Moodle-based platform at University POLITEHNICA of Bucharest). It consists of two main components:

1. **Numerical feedback processing** — Reads raw feedback spreadsheets (`.xls`/`.csv`), computes per-course, per-professor, and per-assistant averages and statistics, and exports the results as processed spreadsheets.

2. **Text categorization** — Automatically classifies free-text student comments (positive, negative, suggestions) into 9 categories (`profesor`, `asistent`, `curs`, `laborator`, `teme`, `examen`, `materiale`, `pozitiv`, `negativ`) using a two-level approach:
   - **Local keyword matching** (`text_categorizer.py`) — Fast, zero-cost classification using a keyword database (`keywords_db.json`). Handles the majority of texts.
   - **LLM fallback** (`llm_client.py`) — Sends remaining uncategorized texts to the Google Gemini API for context-aware classification. Also suggests new keywords to improve future local matching.

### How to Run

#### 1. Setup the virtual environment

The project needs a Python virtual environment to install dependencies without breaking the system Python.

```bash
cd process-feedback/

# Create the virtual environment (only once)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

> **Note:** Every time you open a new terminal, you need to activate the venv again with `source venv/bin/activate`, or use `./venv/bin/python3` directly.

#### 2. Configure the Gemini API key (optional)

If you want the LLM fallback (Gemini) to work, create a `.env` file:

```bash
# In process-feedback/ directory
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

The `.env` file is already in `.gitignore`, so it won't be committed.

Without a Gemini API key, the system works using only the local keyword matching — the Gemini tests will be skipped automatically.

#### 3. Run the tests

```bash
cd process-feedback/

# Option A: If venv is activated
python3 test_categorizer.py

# Option B: Without activating venv
./venv/bin/python3 test_categorizer.py
```

#### 4. Verify the output

If everything works, you should see output like this:

```
Running categorizer tests...

  Testing categorize_text() — simple texts...
    OK: 'Profesorul explica foarte bine' -> ['profesor', 'pozitiv']
    OK: 'Laboratorul e prost organizat' -> ['laborator', 'negativ']
    OK: 'Examenul a fost greu' -> ['examen', 'negativ']
    OK: Empty text -> []
    OK: None text -> []
    OK: Text with diacritics -> ['profesor', 'curs', 'pozitiv']
    OK: Whitespace only -> []
  PASSED: categorize_text() — simple texts

  Testing categorize_text() — multi-category texts...
    OK: prof + curs + pozitiv -> ['profesor', 'curs', 'pozitiv']
    OK: teme + laborator (sentiments dropped via conflict) -> ['laborator', 'teme']
    OK: materiale + curs + pozitiv -> ['curs', 'materiale', 'pozitiv']
    OK: asistent + examen + pozitiv -> ['asistent', 'examen', 'pozitiv']
  PASSED: categorize_text() — multi-category texts

  Testing categorize_text() — long realistic texts...
    ...
  PASSED: categorize_text() — long realistic texts

  Testing negation and conflict detection...
    OK: 'nu preda bine' -> [] (negation detected)
    OK: 'Nu mi-a placut cursul deloc' -> [] (negation detected)
    OK: 'Profesorul nu explica bine materia' -> [] (negation detected)
    OK: Negation with diacritics -> [] (negation detected)
    OK: 'numar' does NOT trigger negation -> ['teme', 'pozitiv']
    OK: 'minunat' does NOT trigger negation -> ['curs', 'pozitiv']
    OK: 'anunt' does NOT trigger negation -> ['examen', 'pozitiv']
    OK: Conflict detected, sentiments dropped, topics kept -> ['curs', 'examen']
    OK: Pure sentiment conflict -> [] (fully uncategorized)
    OK: Single pozitiv sentiment works normally -> ['curs', 'pozitiv']
    OK: Single negativ sentiment works normally -> ['laborator', 'negativ']
    OK: categorize_all_texts integration -> 2 categorized, 2 uncategorized
  PASSED: negation and conflict detection

  Testing categorize_all_texts()...
    ...
  PASSED: categorize_all_texts()

  Testing update_keywords()...
    OK: New words added successfully
    OK: No duplicates created
    OK: New category created with words
    OK: Multiple words added to multiple categories
    OK: Original DB restored
  PASSED: update_keywords()

  Testing analyze_with_gemini()...
    SKIPPED: GEMINI_API_KEY not set in environment    # <-- normal without API key

  Testing full flow...
    Local: 3 categorized, 3 uncategorized
    SKIPPED Gemini step: no API key
  PASSED: full flow

All tests passed (or skipped).
```

> If `analyze_with_gemini` shows `SKIPPED`, that's normal — it means the API key is missing or `python-dotenv` is not installed.

#### 5. Numerical processing (spreadsheets)

This is the older numerical pipeline — not related to text categorization. Replace `data/` with your actual data folder:

```bash
cd process-feedback/
mkdir data/                                # Create a folder for your data
cp /path/to/feedback.xls data/             # Copy the raw spreadsheet there
./xls2csv.sh data/                         # Convert .xls to .csv
./process_feedback.py data/                # Process and generate results
./csv2xlsx data/                           # Convert results to .xlsx
```

#### 6. Troubleshooting

| Problem | Solution |
|---------|----------|
| `pip install` fails with "externally-managed-environment" | Use a venv (see step 1) |
| `analyze_with_gemini` is SKIPPED | Create `.env` with `GEMINI_API_KEY=...` and install `python-dotenv` |
| `ModuleNotFoundError: google.genai` | Run `pip install google-genai` inside the venv |
| `GEMINI_API_KEY not found` | Check that `.env` exists in `process-feedback/` and contains the key |
