import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Influencer Discovery Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Influencer Discovery Dashboard")

st.write(
    "Upload an influencer dataset and find creators matching your selected criteria."
)

st.divider()

st.subheader("Search Criteria")

# Layout
col1, col2 = st.columns(2)

with col1:
    language = st.selectbox(
        "Language",
        ["Hindi", "English", "Hindi & English"]
    )

with col2:
    orientation = st.selectbox(
        "Orientation",
        ["Pro Government", "Neutral", "Any"]
    )

niche = st.text_input(
    "Content Niche",
    placeholder="Example: Government Schemes, Digital India"
)

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

analyze = st.button("Analyze Influencers")



if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Name",
            "Handle",
            "Platform",
            "Bio",
            "Followers",
            "Language"
        ]

        missing_columns = []

        for column in required_columns:
            if column not in df.columns:
                missing_columns.append(column)

        if missing_columns:
            st.error("Invalid CSV File")
            st.write("Missing Columns:")
            st.write(missing_columns)

        else:
            st.success("Valid CSV File")

            st.subheader("Uploaded Data")

            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error : {e}")