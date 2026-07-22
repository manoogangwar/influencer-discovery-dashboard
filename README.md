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
