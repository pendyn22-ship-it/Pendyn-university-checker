import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WASSCE University Eligibility Checker",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Pendyn's University Checker")
st.write("Enter your WASSCE aggregate and search for specific courses or filter by university (2027 Cycle).")

@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load cutoffs.csv. Error: {e}")
    st.stop()

# Controls Container
with st.container(border=True):
    st.subheader("1️⃣ Enter Your Details & Search")
    
    user_aggregate = st.number_input(
        "Your Best 6 WASSCE Aggregate (6 to 36)",
        min_value=6,
        max_value=36,
        value=12,
        step=1
    )

    # Search Bar for specific course names
    search_query = st.text_input(
        "🔍 Search Course Name (Optional)",
        placeholder="e.g., Computer, Nursing, Law, Business...",
        help="Type any keyword to instantly filter course titles."
    )

    col1, col2 = st.columns(2)
    with col1:
        selected_uni = st.selectbox(
            "Filter by University",
            ["All Universities"] + sorted(list(df["University"].unique()))
        )
    with col2:
        selected_cat = st.selectbox(
            "Filter by Field of Study",
            ["All Fields"] + sorted(list(df["Category"].unique()))
        )

# Apply Filters & Search Query
filtered_df = df.copy()
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]
if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]
if search_query:
    filtered_df = filtered_df[filtered_df["Course"].str.contains(search_query, case=False, na=False)]

# Eligibility logic
eligible_df = filtered_df[filtered_df["Cutoff"] >= user_aggregate].sort_values(by="Cutoff")

st.subheader("2️⃣ Your Results")

tab1, tab2 = st.tabs([
    f"✅ Qualified Courses ({len(eligible_df)})",
    f"📋 All Listed Cut-Offs ({len(filtered_df)})"
])

with tab1:
    if not eligible_df.empty:
        st.success(f"With **Aggregate {user_aggregate}**, you meet the cut-off for **{len(eligible_df)}** programme(s):")
        st.dataframe(
            eligible_df[["University", "Course", "Category", "Cutoff"]],
            hide_index=True,
            width="stretch"
        )
    else:
        st.warning(f"No programmes match your search or aggregate threshold of **{user_aggregate}**.")

with tab2:
    st.write("Compare all programmes matching your filters:")
    display_all = filtered_df.copy()
    display_all["Status"] = display_all["Cutoff"].apply(
        lambda c: "✅ Eligible" if c >= user_aggregate else "❌ Above Cut-off"
    )
    st.dataframe(
        display_all[["University", "Course", "Cutoff", "Status"]].sort_values(by="Cutoff"),
        hide_index=True,
        width="stretch"
    )




