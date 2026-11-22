import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WASSCE University Eligibility Checker",
    page_icon="🎓",
    layout="centered"
)

# Header & Clear Instructions
st.title("🎓 Pendyn's University Checker")
st.write("Enter your WASSCE aggregate below to instantly see which Ghanaian university programmes you qualify for (2027 Cycle).")
st.caption("💡 Remember: In WASSCE grading, a **lower aggregate** is better (e.g., Aggregate 6 is higher than Aggregate 15).")

@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load cutoffs.csv. Error: {e}")
    st.stop()

# Main-Screen Controls (Easy to see on mobile without opening a sidebar)
with st.container(border=True):
    st.subheader("1️⃣ Enter Your Details")
    user_aggregate = st.number_input(
        "Your Best 6 WASSCE Aggregate (6 to 36)",
        min_value=6,
        max_value=36,
        value=12,
        step=1,
        help="Add your 3 core subjects (English, Core Maths, Integrated Science/Social Studies) + your 3 best electives."
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

# Apply filters
filtered_df = df.copy()
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]
if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

# Eligibility logic: user's aggregate must be <= cutoff
eligible_df = filtered_df[filtered_df["Cutoff"] >= user_aggregate].sort_values(by="Cutoff")

st.subheader("2️⃣ Your Results")

# Organize output into clean tabs so students aren't overwhelmed
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
        st.warning(f"No programmes in this filter accept **Aggregate {user_aggregate}**.")
        st.info("💡 Try selecting **All Universities** or **All Fields** above, or explore universities with more flexible cut-offs like UDS, UEW, or UCC.")

with tab2:
    st.write("Compare all programmes in your selected filter:")
    display_all = filtered_df.copy()
    display_all["Status"] = display_all["Cutoff"].apply(
        lambda c: "✅ Eligible" if c >= user_aggregate else "❌ Above Cut-off"
    )
    st.dataframe(
        display_all[["University", "Course", "Cutoff", "Status"]].sort_values(by="Cutoff"),
        hide_index=True,
        width="stretch"
    )



