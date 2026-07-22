# Influencer Discovery Dashboard

A Streamlit app for uploading influencer datasets, validating required fields, and scoring creators against selected language, orientation, and niche criteria.

## Features

- CSV upload and validation
- Automated influencer scoring
- Matched keyword extraction
- Filter and sort analysis results

## Installation

1. Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

## CSV format

The uploaded CSV file must contain the following columns:

- `Name`
- `Handle`
- `Platform`
- `Bio`
- `Followers`
- `Language`

## Notes

- Use the sidebar to choose language, orientation, and niche.
- After analysis, filter by platform, score, and sorting preference.

## Approach & Write-up

This project uses a lightweight keyword-and-heuristic approach to score influencers against selected criteria (language, orientation, niche).

- Input: a CSV or Excel file with columns `Name`, `Handle`, `Platform`, `Bio`, `Followers`, `Language`.
- Parsing: `pandas` reads CSV/XLSX uploads and `validator.py` ensures required columns are present.
- Classification: `classifier.py` normalizes the influencer `Bio` and checks for niche-related terms (user-provided keywords) and a set of orientation keywords (e.g., "government", "digital india", "make in india"). Scores are computed as:
	- Niche match: up to 40 points (proportional to matched niche terms)
	- Language match: up to 30 points
	- Orientation match: up to 30 points

The final score (0–100) is bucketed into `Excellent`, `Good`, `Average`, and `Poor` for quick interpretation. Matches and matched keywords are shown alongside follower counts so analysts can verify results.

Assumptions:
- Influencer language is present in the `Language` column and uses simple labels like "Hindi" or "English".
- Bios are representative of content; keyword presence in Bio is used as the primary signal.
- This is a deterministic, explainable approach intended for prototyping; an LLM-based classifier can be added for richer semantic matching.

## Sample run / demo

1. Start the app:

```bash
streamlit run app.py
```

2. In the sidebar select `Language` = `Hindi` or `English` (or both), `Orientation` = `Pro Government`, and set `Content Niche` to something like `Government Schemes, Digital India`.
3. Upload the provided `data.csv` and click `Analyze Influencers`.

The app will display the uploaded data, analyzed results with `Match Score`, `Matched Keywords`, `Status`, and allow filtering/sorting by platform, score, and followers.

## Files of interest

- `app.py` — Streamlit frontend and orchestration
- `classifier.py` — scoring logic and keyword lists
- `validator.py` — CSV schema checks
- `utils.py` — helpers for normalization and follower parsing
- `data.csv` — small sample dataset demonstrating criteria matches

If you want, I can extend `classifier.py` to use an LLM API (OpenAI, local LLM) for semantic matching — tell me which provider and API key approach you'd prefer.
