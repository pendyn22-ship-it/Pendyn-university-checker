import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Pendyn's University Checker 2027", page_icon="🎓", layout="centered")

# Custom CSS for your exact green styling and cards
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
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
        font-size: 1.7rem;
    }
    .header-banner p {
        color: #e8f5e9;
        margin: 0;
        font-size: 0.9rem;
    }
    .filter-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.2rem;
    }
    .ai-advisor-card {
        background-color: #f1f8f5;
        border-left: 5px solid #2e7d32;
        padding: 1.2rem;
        border-radius: 8px;
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

# Top Header Banner
st.markdown("""
    <div class="header-banner">
        <h1>🎓 Pendyn's University Checker 2027</h1>
        <p>Calculate aggregates, analyze admission chances, check subject prerequisites, and share your choices via WhatsApp.</p>
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

# --- SECTION 1: ENTER AGGREGATE & FILTER ---
st.markdown("### 1️⃣ Enter Aggregate & Filter")

with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    
    user_aggregate = st.number_input("Your Best 6 WASSCE Aggregate (6 to 36)", min_value=6, max_value=36, value=6, step=1)
    
    search_query = st.text_input("🔍 Search Course Name (Optional)", placeholder="e.g., Computer science, Nursing, Building Technology")

    col1, col2 = st.columns(2)
    with col1:
        universities = ["All Universities"] + sorted(df["University"].unique().tolist())
        selected_uni = st.selectbox("Filter by University", universities)

    with col2:
        categories = ["All Fields"] + sorted(df["Category"].unique().tolist())
        selected_cat = st.selectbox("Filter by Field of Study", categories)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILTERING LOGIC ---
filtered_df = df.copy()

# Multi-keyword flexible search (OR logic)
if search_query:
    keywords = search_query.strip().split()
    pattern = "|".join(keywords)
    filtered_df = filtered_df[filtered_df["Course"].str.contains(pattern, case=False, na=False)]

if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]

if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]

# Direct Eligibility (user_aggregate <= Cutoff)
qualified_df = filtered_df[user_aggregate <= filtered_df["Cutoff"]].sort_values(by=["Cutoff", "University"])

# --- SECTION 2: YOUR RESULTS & AI ADVISOR SUMMARY ---
st.markdown("### 2️⃣ Your Results & AI Advisor Summary")

# AI Advisor Card Box matching your video design
st.markdown(f"""
    <div class="ai-advisor-card">
        <h4 style="margin-top:0; color:#1b5e20;">💬 Advisor Response for Aggregate {user_aggregate}</h4>
        <p style="margin-bottom:0;">
            Based on your <b>Aggregate {user_aggregate}</b>, you qualify for <b>{len(qualified_df)}</b> programme(s) across <b>{qualified_df['University'].nunique() if not qualified_df.empty else 0}</b> institution(s) in your current search! 
            📋 Check Tab 2 below to lock in your Top 3 Choices & share via WhatsApp!
        </p>
    </div>
""", unsafe_allow_html=True)

# Metrics Display
m1, m2 = st.columns(2)
m1.metric("🎯 Your Aggregate", user_aggregate)
m2.metric("✅ Qualified Courses", len(qualified_df))

# Tabs matching your video interface
tab1, tab2 = st.tabs(["✅ Qualified Cards (" + str(len(qualified_df)) + ")", "🏆 Top 3 Choices & Share"])

with tab1:
    st.markdown("Tap any course below to check its admission outlook and career path:")
    
    if not qualified_df.empty:
        for idx, row in qualified_df.iterrows():
            with st.expander(f"🏛️ {row['University']} — {row['Course']} (Cut-off: {row['Cutoff']})"):
                st.write(f"**Field of Study:** {row['Category']}")
                st.write(f"**Your Aggregate:** {user_aggregate} (Eligible requirement: ≤ {row['Cutoff']})")
                st.success("You meet the regular admission cutoff for this program!")
        
        # Download button
        st.markdown("---")
        csv_export = qualified_df[["University", "Course", "Category", "Cutoff"]].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Qualified Courses (CSV)",
            data=csv_export,
            file_name=f"Pendyn_Qualified_Courses_Agg_{user_aggregate}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No courses match your current search and aggregate criteria. Try adjusting your search or selecting 'All Universities'.")

with tab2:
    st.markdown("### 🏆 Your Top 3 Selection & WhatsApp Share")
    st.markdown("Select and lock in your top choices to share with parents or advisors:")
    
    if not qualified_df.empty:
        top_choices = qualified_df.head(3)
        for i, row in top_choices.reset_index(drop=True).iterrows():
            st.markdown(f"**Choice {i+1}:** {row['University']} — {row['Course']} (Cut-off: {row['Cutoff']})")
        
        # WhatsApp sharing helper text
        courses_text = "%0A".join([f"{i+1}. {row['University']} - {row['Course']}" for i, row in top_choices.reset_index(drop=True).iterrows()])
        whatsapp_url = f"https://api.whatsapp.com/send?text=Hi!%20Here%20are%20my%20Top%203%20University%20Choices%20for%20WASSCE%20Aggregate%20{user_aggregate}:%0A{courses_text}"
        
        st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank">
                <button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:1rem; margin-top:10px;">
                    💬 Share Top Choices via WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)
    else:
        st.info("Unlock qualified courses above to generate your Top 3 choices.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 0.85rem;'>Built by Pendyn • Always verify final cut-offs against official 2027 university admission brochures.</p>", unsafe_allow_html=True)
