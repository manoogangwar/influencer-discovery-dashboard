import pandas as pd
import streamlit as st
import requests

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
    # default: without using LLM
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

    # Export filtered results as CSV
    try:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered results (CSV)", data=csv, file_name="filtered_influencers.csv", mime="text/csv")
    except Exception:
        st.warning("Unable to prepare CSV for download.")


def render_cards(df, page: int, page_size: int):
    """Render a paginated card view for the dataframe."""
    start = page * page_size
    end = start + page_size
    page_df = df.reset_index(drop=True).iloc[start:end]

    if page_df.empty:
        st.info("No results on this page.")
        return

    # Display cards in rows of three
    cols_per_row = 3
    for i in range(0, len(page_df), cols_per_row):
        row_slice = page_df.iloc[i : i + cols_per_row]
        cols = st.columns(len(row_slice))
        for col, (_, r) in zip(cols, row_slice.iterrows()):
            with col:
                st.markdown(f"**{r.get('Name','')}**")
                handle = r.get('Handle', '')
                platform = r.get('Platform', '')
                if handle:
                    st.write(f"@{handle}")
                st.write(f"**Platform:** {platform}")
                st.write(f"**Followers:** {r.get('Followers', '')}")
                st.write(f"**Match Score:** {r.get('Match Score', '')} — {r.get('Status','')}")
                keywords = r.get('Matched Keywords', '')
                if keywords:
                    st.write(f"**Matched:** {keywords}")
                bio = r.get('Bio', '')
                if bio:
                    st.caption(bio[:200])


def main():
    st.set_page_config(page_title="Influencer Discovery Dashboard", page_icon="📊", layout="wide")
    st.title("📊 Influencer Discovery Dashboard")
    st.write("Upload an influencer dataset and find creators matching your selected criteria.")
    st.divider()

    if "result_df" not in st.session_state:
        st.session_state.result_df = None

    with st.sidebar:
        st.header("Search Criteria")
        mode = st.radio("Mode", ["Upload File", "Live Search"], index=0)

        language = st.selectbox("Language", ["Hindi", "English", "Hindi & English"])
        orientation = st.selectbox("Orientation", ["Pro Government", "Neutral", "Any"])
        niche = st.text_input("Content Niche", placeholder="Example: Government Schemes, Digital India")

        st.divider()
        st.subheader("LLM (optional)")
        use_llm = st.checkbox("Use LLM semantic matching (OpenAI)")
        api_key = None
        if use_llm:
            api_key = st.text_input("OpenAI API Key (optional)", type="password")

        st.divider()
        uploaded_file = None
        live_df = None
        analyze = False

        if mode == "Upload File":
            uploaded_file = st.file_uploader("Upload your influencer CSV or Excel", type=["csv", "xls", "xlsx"])
            analyze = st.button("Analyze Influencers")
        else:
            st.subheader("Live Search")
            platform = st.selectbox("Platform", ["YouTube"])
            query = st.text_input("Search query / keywords", placeholder="e.g. government schemes, digital india")
            max_results = st.slider("Max results", 1, 50, 10)
            yt_api_key = st.text_input("YouTube API Key (required for live search)")
            search_now = st.button("Search")
            if search_now:
                if platform == "YouTube":
                    try:
                        live_df = fetch_youtube_channels(query, yt_api_key, max_results)
                        st.success(f"Fetched {len(live_df)} results from YouTube")
                    except Exception as exc:
                        st.error(f"Live search failed: {exc}")
                analyze = st.button("Analyze Live Results")

    # If using Live Search and we have live_df, use it as the dataset
    if uploaded_file is None and 'live_df' in locals() and live_df is not None:
        df = live_df
    else:
        if uploaded_file is None:
            st.info("Upload a CSV file or perform a live search to continue.")
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

        # View mode: table or cards
        view_mode = st.radio("View As", ["Table", "Cards"], horizontal=True)
        # Pagination controls
        total = len(st.session_state.result_df)
        page_size = st.selectbox("Results per page", [3, 6, 9, 12, 24], index=1)
        total_pages = max(1, (total + page_size - 1) // page_size)
        if "page" not in st.session_state:
            st.session_state.page = 0

        cols = st.columns([1, 2, 1])
        with cols[0]:
            if st.button("Prev"):
                st.session_state.page = max(0, st.session_state.page - 1)
        with cols[2]:
            if st.button("Next"):
                st.session_state.page = min(total_pages - 1, st.session_state.page + 1)

        st.write(f"Page {st.session_state.page + 1} of {total_pages} — {total} results")

        if view_mode == "Table":
            st.dataframe(st.session_state.result_df, use_container_width=True)
        else:
            render_cards(st.session_state.result_df, st.session_state.page, page_size)

        render_filters(st.session_state.result_df)


def fetch_youtube_channels(query, api_key, max_results=10):
    """Fetch YouTube channels matching query and return a DataFrame with required columns.

    Columns: Name, Handle, Platform, Bio, Followers, Language
    """
    if not api_key:
        raise ValueError("YouTube API key is required for live search")
    if not query:
        raise ValueError("Query cannot be empty for live search")

    search_url = "https://www.googleapis.com/youtube/v3/search"
    channels_url = "https://www.googleapis.com/youtube/v3/channels"

    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": min(50, max_results),
        "key": api_key,
    }

    resp = requests.get(search_url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])

    rows = []
    channel_ids = [it["snippet"]["channelId"] for it in items if it.get("snippet")]
    if channel_ids:
        # fetch channel statistics
        cparams = {"part": "snippet,statistics", "id": ",".join(channel_ids), "key": api_key}
        cresp = requests.get(channels_url, params=cparams, timeout=15)
        cresp.raise_for_status()
        cdata = cresp.json()
        for ch in cdata.get("items", []):
            snip = ch.get("snippet", {})
            stats = ch.get("statistics", {})
            name = snip.get("title", "")
            handle = ch.get("id", "")
            platform = "YouTube"
            bio = snip.get("description", "")
            followers = convert_to_int(stats.get("subscriberCount", 0))
            language = ""
            rows.append({"Name": name, "Handle": handle, "Platform": platform, "Bio": bio, "Followers": followers, "Language": language})

    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()

        