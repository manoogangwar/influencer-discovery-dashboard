REQUIRED_COLUMNS = [
    "Name",
    "Handle",
    "Platform",
    "Bio",
    "Followers",
    "Language",
]


def validate_dataframe(df):
    """Validate uploaded CSV and return any missing columns."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    return missing_columns
