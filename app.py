import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pendyn's University Checker", page_icon="🎓", layout="centered")

st.title("🎓 Pendyn's University Checker 2027")
st.markdown("Find out your eligibility across all Ghanaian public, technical, and specialized universities based on your WASSCE aggregate.")

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'cutoffs.csv' file not found. Please make sure it is uploaded in your repository.")
    st.stop()

# Sidebar / Filters
st.sidebar.header("🔍 Filter Options")

# University Filter
universities = ["All Universities"] + sorted(df["University"].unique().tolist())
selected_uni = st.sidebar.selectbox("Filter by University", universities)

# Field / Category Filter
categories = ["All Fields"] + sorted(df["Category"].unique().tolist())
selected_cat = st.sidebar.selectbox("Filter by Field of Study", categories)

# User Input: WASSCE Aggregate
st.markdown("### 🎯 Enter Your Aggregate")
user_aggregate = st.number_input("Your Best 6 Subjects Aggregate", min_value=6, max_value=36, value=10, step=1)

# Search Bar Input
search_query = st.text_input("Search Course (e.g., Computer Science, Architecture, Accounting)")

# Filtering Logic
filtered_df = df.copy()

# 1. Apply Search Query with Keyword Splitting (Fixes multi-word and partial search issues)
if search_query:
    keywords = search_query.strip().split()
    query_filter = filtered_df.copy()
    for kw in keywords:
        query_filter = query_filter[query_filter["Course"].str.contains(kw, case=False, na=False)]
    filtered_df = query_filter

# 2. Apply University Filter
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]

# 3. Apply Category Filter
if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

# 4. Apply Eligibility Logic (WASSCE inverse logic: user aggregate must be <= cutoff requirement)
qualified_df = filtered_df[user_aggregate <= filtered_df["Cutoff"]]

# Display Results
st.markdown("---")
st.markdown(f"### 📊 Results (Your Aggregate: {user_aggregate})")
st.metric(label="Qualified Courses Found", value=len(qualified_df))

if not qualified_df.empty:
    st.dataframe(qualified_df[["University", "Course", "Category", "Cutoff"]], use_container_width=True)
else:
    st.warning("No courses match your criteria or aggregate threshold. Try adjusting your search or aggregate value!")
