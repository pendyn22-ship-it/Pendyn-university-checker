import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pendyn's University Checker 2027", page_icon="🎓", layout="centered")

# Custom CSS for Card Layout & Green Styling
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f5;
    }
    .header-banner {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    .header-banner h1 {
        color: white !important;
        margin-bottom: 0.3rem;
        font-size: 1.8rem;
    }
    .header-banner p {
        color: #e8f5e9;
        margin: 0;
        font-size: 0.95rem;
    }
    .filter-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
    }
    .stDownloadButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
    }
    .stDownloadButton > button:hover {
        background-color: #1b5e20 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
    <div class="header-banner">
        <h1>🎓 Pendyn's University Checker 2027</h1>
        <p>Check your eligibility across 46 Ghanaian public, technical, and private universities based on your WASSCE results.</p>
    </div>
""", unsafe_allow_html=True)

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: 'cutoffs.csv' file not found. Please make sure it is uploaded in your repository.")
    st.stop()

# --- INPUT & FILTER CARD ---
with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    
    col_agg, col_core = st.columns([1, 1])
    with col_agg:
        user_aggregate = st.number_input("🎯 Your Best 6 WASSCE Aggregate (6 to 36)", min_value=6, max_value=36, value=12, step=1)
    with col_core:
        # Feature 2: Core Subject Credit Check
        has_core_issue = st.selectbox(
            "📋 Core Subjects Status (English, Maths, Science, Social)",
            ["All A1–C6 (Credit Passes)", "I have D7, E8, or F9 in a Core Subject"]
        )

    search_query = st.text_input("🔎 Search Course Name (Optional)", placeholder="e.g., Computer Science, Nursing, Building Technology")

    col1, col2 = st.columns(2)
    with col1:
        universities = ["All Universities"] + sorted(df["University"].unique().tolist())
        selected_uni = st.selectbox("🏫 Filter by University", universities)

    with col2:
        categories = ["All Fields"] + sorted(df["Category"].unique().tolist())
        selected_cat = st.selectbox("📚 Filter by Field of Study", categories)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- FEATURE 2: CORE SUBJECT CREDIT ALERT ---
if has_core_issue == "I have D7, E8, or F9 in a Core Subject":
    st.error(
        "⚠️ **Core Subject Alert (D7 / E8 / F9 Detected):** Most public universities (UG, KNUST, UCC, UHAS, UPSA) strictly require **A1–C6 credit passes** in English Language, Core Mathematics, Integrated Science, and Social Studies for regular degree admission—even if your overall aggregate is strong. "
        "Consider **Diploma / HND pathways at Technical Universities**, **Certificate-to-Degree bridging programs**, or **Private Universities** that accept D7 in specific non-core electives."
    )

# --- FILTERING LOGIC ---
filtered_df = df.copy()

# 1. Multi-keyword search (OR logic so partial multi-word searches match flexibly)
if search_query:
    keywords = search_query.strip().split()
    pattern = "|".join(keywords)
    filtered_df = filtered_df[filtered_df["Course"].str.contains(pattern, case=False, na=False)]

# 2. University filter
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]

# 3. Field of study filter
if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

# 4. Direct Eligibility (user_aggregate <= Cutoff)
qualified_df = filtered_df[user_aggregate <= filtered_df["Cutoff"]].sort_values(by=["Cutoff", "University"])

# 5. Feature 3: Close Call / Fee-Paying Alternatives (Missed cutoff by 1 to 3 points)
close_call_df = filtered_df[
    (filtered_df["Cutoff"] < user_aggregate) & 
    (filtered_df["Cutoff"] >= user_aggregate - 3)
].sort_values(by=["Cutoff", "University"])

# --- METRICS SUMMARY ---
st.markdown("### 2️⃣ Your Results & AI Advisor Summary")
m1, m2, m3 = st.columns(3)
m1.metric("🎯 Your Aggregate", user_aggregate)
m2.metric("✅ Qualified Courses", len(qualified_df))
m3.metric("🏫 Matching Schools", qualified_df["University"].nunique() if not qualified_df.empty else 0)

# --- DIRECT QUALIFIED COURSES ---
st.markdown("#### ✅ Directly Qualified Programs")
if not qualified_df.empty:
    st.success(f"Great news! You meet the regular cutoff for **{len(qualified_df)}** program(s).")
    st.dataframe(
        qualified_df[["University", "Course", "Category", "Cutoff"]].reset_index(drop=True),
        use_container_width=True
    )
    
    # --- FEATURE 4: DOWNLOADABLE RESULTS SLIP ---
    csv_export = qualified_df[["University", "Course", "Category", "Cutoff"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download My Qualified Courses Slip (CSV)",
        data=csv_export,
        file_name=f"Pendyn_Eligible_Courses_Agg_{user_aggregate}.csv",
        mime="text/csv"
    )
else:
    st.warning("No regular courses matched your exact aggregate and filters. Check the 'Close Call' options below or widen your filters!")

# --- FEATURE 3: CLOSE CALL & FEE-PAYING ALTERNATIVES ---
if not close_call_df.empty:
    st.markdown("---")
    st.markdown("#### ⚡ Close Calls & Fee-Paying / Parallel Alternatives (1–3 Points Away)")
    st.info(
        "💡 **Tip:** You missed the regular cutoffs below by just **1 to 3 points**. "
        "Many Ghanaian universities offer **Fee-Paying** or **Parallel** admission slots for applicants within this range!"
    )
    close_display = close_call_df[["University", "Course", "Category", "Cutoff"]].copy()
    close_display["Points Away"] = user_aggregate - close_display["Cutoff"]
    st.dataframe(close_display.reset_index(drop=True), use_container_width=True)
