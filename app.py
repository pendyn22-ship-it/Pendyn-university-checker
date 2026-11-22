import pandas as pd
import streamlit as st

st.set_page_config(page_title="WASSCE University Eligibility Checker", page_icon="🎓")

st.title("🎓 Pendyn's University Checker")
st.write("Check your WASSCE aggregate eligibility for top Ghanaian universities based on official 2027 cut-off points.")

# Load dataset safely with caching
@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load cutoffs.csv. Make sure it is in your repository. Error: {e}")
    st.stop()

# Sidebar filters & user inputs
st.sidebar.header("Your Details")
user_aggregate = st.sidebar.number_input(
    "Enter your WASSCE Aggregate", min_value=6, max_value=48, value=10, step=1
)

selected_uni = st.sidebar.selectbox(
    "Filter by University", ["All Universities"] + list(df["University"].unique())
)

# Filter dataframe based on user selection
filtered_df = df.copy()
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]

# Main view: Eligibility checking logic
st.subheader("📋 Available Courses & Cut-offs")

# Check eligibility column: user aggregate must be <= cutoff
filtered_df["Eligible"] = filtered_df["Cutoff"] >= user_aggregate

# Display results table with custom formatting
st.dataframe(
    filtered_df[["University", "Course", "Cutoff", "Eligible"]],
    use_container_width=True,
)

# Summary of matched options
eligible_courses = filtered_df[filtered_df["Eligible"] == True]

st.markdown("---")
st.subheader("🎯 Your Admission Status")
if not eligible_courses.empty:
    st.success(f"Great news! With an aggregate of **{user_aggregate}**, you qualify for **{len(eligible_courses)}** courses in this list!")
    with st.expander("View courses you qualify for"):
        for index, row in eligible_courses.iterrows():
            st.write(f"- **{row['University']}**: {row['Course']} (Cut-off: {row['Cutoff']})")
else:
    st.warning(f"An aggregate of **{user_aggregate}** is higher than the listed cut-offs for these specific programs. Consider checking broader backup options or fee-paying pathways.")


