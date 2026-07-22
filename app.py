import pandas as pd
import streamlit as st

from classifier import classify_influencer
from utils import convert_to_int
from validator import validate_dataframe


def load_dataset(uploaded_file):
    # Support CSV and Excel uploads
    name = getattr(uploaded_file, "name", "") or ""
    name = name.lower()
    try:
        if name.endswith(('.xls', '.xlsx')):
            dataset = pd.read_excel(uploaded_file)
        else:
            dataset = pd.read_csv(uploaded_file)
    except Exception as exc:
        raise ValueError("Unable to read the uploaded file. Please upload a valid CSV or Excel file.") from exc

    return dataset


def analyze_dataframe(df, language, orientation, niche):
    # default: not using LLM
    result_df = df.copy()
    scores = []
    matched_keywords = []
    statuses = []

    for _, row in result_df.iterrows():
        score, keywords, status = classify_influencer(
            bio=row.get("Bio", ""),
            influencer_language=row.get("Language", ""),
            selected_language=language,
            selected_orientation=orientation,
            selected_niche=niche,
        )
        scores.append(score)
        matched_keywords.append(", ".join(keywords))
        statuses.append(status)

    result_df["Match Score"] = scores
    result_df["Matched Keywords"] = matched_keywords
    result_df["Status"] = statuses
    result_df["Followers"] = result_df["Followers"].apply(convert_to_int)

    return result_df


def render_filters(df):
    st.divider()
    st.subheader("Filter & Sort Results")

    platforms = ["All"] + sorted(df["Platform"].dropna().unique().tolist())
    selected_platform = st.selectbox("Filter by Platform", platforms)

    minimum_score = st.slider("Minimum Match Score", 0, 100, 0)
    sort_by = st.selectbox("Sort By", ["Match Score", "Followers", "Name"])

    filtered_df = df.copy()
    if selected_platform != "All":
        filtered_df = filtered_df[filtered_df["Platform"] == selected_platform]

    filtered_df = filtered_df[filtered_df["Match Score"] >= minimum_score]

    if sort_by == "Match Score":
        filtered_df = filtered_df.sort_values(by="Match Score", ascending=False)
    elif sort_by == "Followers":
        filtered_df = filtered_df.sort_values(by="Followers", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="Name")

    st.subheader("Filtered Results")
    st.dataframe(filtered_df, use_container_width=True)


def main():
    st.set_page_config(page_title="Influencer Discovery Dashboard", page_icon="📊", layout="wide")
    st.title("📊 Influencer Discovery Dashboard")
    st.write("Upload an influencer dataset and find creators matching your selected criteria.")
    st.divider()

    if "result_df" not in st.session_state:
        st.session_state.result_df = None

    with st.sidebar:
        st.header("Search Criteria")
        language = st.selectbox("Language", ["Hindi", "English", "Hindi & English"])
        orientation = st.selectbox("Orientation", ["Pro Government", "Neutral", "Any"])
        niche = st.text_input("Content Niche", placeholder="Example: Government Schemes, Digital India")
        use_llm = st.checkbox("Use LLM semantic matching (OpenAI)")
        api_key = None
        if use_llm:
            api_key = st.text_input("OpenAI API Key (optional)", type="password")

        uploaded_file = st.file_uploader("Upload your influencer CSV or Excel", type=["csv", "xls", "xlsx"])
        analyze = st.button("Analyze Influencers")

    if uploaded_file is None:
        st.info("Upload a CSV file to continue.")
        return

    try:
        df = load_dataset(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        return

    missing_columns = validate_dataframe(df)
    if missing_columns:
        st.error("Invalid CSV file.")
        st.error("Missing columns: " + ", ".join(missing_columns))
        return

    st.success("Valid CSV file.")
    st.subheader("Uploaded Data")
    st.dataframe(df, use_container_width=True)

    if analyze:
        # If LLM selected, use LLM wrapper
        if use_llm and api_key:
            # call classifier's LLM wrapper during analysis
            result_df = df.copy()
            scores = []
            matched_keywords = []
            statuses = []
            from classifier import classify_influencer_llm

            for _, row in result_df.iterrows():
                score, keywords, status = classify_influencer_llm(
                    bio=row.get("Bio", ""),
                    influencer_language=row.get("Language", ""),
                    selected_language=language,
                    selected_orientation=orientation,
                    selected_niche=niche,
                    api_key=api_key,
                )
                scores.append(score)
                matched_keywords.append(", ".join(keywords))
                statuses.append(status)

            result_df["Match Score"] = scores
            result_df["Matched Keywords"] = matched_keywords
            result_df["Status"] = statuses
            result_df["Followers"] = result_df["Followers"].apply(convert_to_int)
        else:
            result_df = analyze_dataframe(df, language, orientation, niche)
        st.session_state.result_df = result_df

    if st.session_state.result_df is not None:
        st.subheader("Analyzed Data")
        st.dataframe(st.session_state.result_df, use_container_width=True)
        render_filters(st.session_state.result_df)


if __name__ == "__main__":
    main()

        