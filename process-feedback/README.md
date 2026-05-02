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

### New & Modified Files

- `keywords_db.json` — keyword database per category (editable)
- `text_categorizer.py` — local keyword-based categorizer
- `llm_client.py` — Gemini API client (requires `.env` with `GEMINI_API_KEY`)
- `test_categorizer.py` — tests for the categorization module
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
