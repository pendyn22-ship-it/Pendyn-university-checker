import io
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pendyn's University Checker",
    page_icon="🎓",
    layout="centered"
)

# --- CUSTOM HERO BANNER ---
st.markdown("""
    <div style="
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 24px 20px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    ">
        <div style="font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #FCD116; margin-bottom: 6px;">
            🇬🇭 2027 WASSCE Admissions Powerhouse
        </div>
        <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #FFFFFF; line-height: 1.2;">
            🎓 Pendyn's University Checker
        </h1>
        <p style="margin: 8px 0 0 0; font-size: 15px; color: #E2E8F0; line-height: 1.4;">
            Calculate aggregates, analyze admission chances, check subject prerequisites, and share your choices via WhatsApp.
        </p>
    </div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load cutoffs.csv. Error: {e}")
    st.stop()

# --- HELPER FUNCTION: CAREER PATHS ---
def get_career_path(course_name):
    c_lower = course_name.lower()
    if "computer" in c_lower or "software" in c_lower or "information" in c_lower or "it" in c_lower:
        return "💻 Software Engineer, Data Analyst, IT Consultant, Cybersecurity Specialist"
    elif "nurs" in c_lower:
        return "🩺 Registered Nurse, Midwife, Healthcare Administrator, Public Health Officer"
    elif "law" in c_lower:
        return "⚖️ Barrister, Solicitor, Corporate Legal Advisor, Policy Analyst"
    elif "medic" in c_lower:
        return "🏥 Medical Doctor, Surgeon, Medical Researcher, Healthcare Consultant"
    elif "business" in c_lower or "admin" in c_lower or "accounting" in c_lower or "finance" in c_lower:
        return "📊 Financial Analyst, Accountant, Corporate Manager, Banker, Entrepreneur"
    elif "engineer" in c_lower:
        return "⚙️ Civil/Mechanical/Electrical Engineer, Project Manager, Technical Consultant"
    elif "agric" in c_lower:
        return "🌱 Agribusiness Manager, Agronomist, Food Security Analyst, Farm Entrepreneur"
    else:
        return "🎓 Professional Practitioner, Researcher, Consultant, Industry Specialist"

# --- FEATURE 1: WASSCE GRADE & PREREQUISITE CALCULATOR ---
with st.expander("📝 WASSCE Aggregate & Subject Prerequisite Calculator"):
    st.write("Select your grades to compute your aggregate and verify core credit requirements.")
    
    grade_points = {"A1": 1, "B2": 2, "B3": 3, "C4": 4, "C5": 5, "C6": 6, "D7": 7, "E8": 8, "F9": 9}
    grade_options = list(grade_points.keys())

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        eng = st.selectbox("Core English", grade_options, index=2, key="calc_eng")
        math = st.selectbox("Core Mathematics", grade_options, index=2, key="calc_math")
    with col_c2:
        sc = st.selectbox("Integrated Science", grade_options, index=2, key="calc_sc")
        soc = st.selectbox("Social Studies", grade_options, index=2, key="calc_soc")

    st.write("Enter your 3 Best Electives:")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.selectbox("Elective 1", grade_options, index=2, key="calc_e1")
    with col_e2:
        e2 = st.selectbox("Elective 2", grade_options, index=2, key="calc_e2")
    with col_e3:
        e3 = st.selectbox("Elective 3", grade_options, index=2, key="calc_e3")

    core_science_val = min(grade_points[sc], grade_points[soc])
    calc_aggregate = grade_points[eng] + grade_points[math] + core_science_val + grade_points[e1] + grade_points[e2] + grade_points[e3]
    
    eng_val = grade_points[eng]
    math_val = grade_points[math]
    core_sc_val = grade_points[sc]
    
    passes_cores = (eng_val <= 6) and (math_val <= 6) and (core_sc_val <= 6)
    
    st.info(f"✨ Calculated Best-6 Aggregate: **{calc_aggregate}**")
    if passes_cores:
        st.success("✅ Core Prerequisite Check: Passed! You meet the standard C6 minimum for core English, Math, and Science.")
    else:
        st.warning("⚠️ Core Prerequisite Check: One or more core subjects fall below C6 (D7–F9). Note that public universities require credit passes in core subjects regardless of aggregate.")

# --- MAIN CONTROLS ---
with st.container(border=True):
    st.subheader("1️⃣ Enter Aggregate & Filter")
    
    user_aggregate = st.number_input(
        "Your Best 6 WASSCE Aggregate (6 to 36)",
        min_value=6,
        max_value=36,
        value=int(calc_aggregate) if 'calc_aggregate' in locals() else 12,
        step=1,
        key="main_user_aggregate_input"
    )

    search_query = st.text_input(
        "🔍 Search Course Name (Optional)",
        placeholder="e.g., Computer, Nursing, Law, Business...",
        key="main_search_query_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        selected_uni = st.selectbox(
            "Filter by University",
            ["All Universities"] + sorted(list(df["University"].unique())),
            key="main_uni_filter"
        )
    with col2:
        selected_cat = st.selectbox(
            "Filter by Field of Study",
            ["All Fields"] + sorted(list(df["Category"].unique())),
            key="main_cat_filter"
        )

# Filter Logic
filtered_df = df.copy()
if selected_uni != "All Universities":
    filtered_df = filtered_df[filtered_df["University"] == selected_uni]
if selected_cat != "All Fields":
    filtered_df = filtered_df[filtered_df["Category"] == selected_cat]
if search_query:
    filtered_df = filtered_df[filtered_df["Course"].str.contains(search_query, case=False, na=False)]

eligible_df = filtered_df[filtered_df["Cutoff"] >= user_aggregate].sort_values(by="Cutoff")

# Add Chance Meter Tag
def assign_chance(row, user_agg):
    diff = row["Cutoff"] - user_agg
    if diff >= 3:
        return "🔥 Safe Bet"
    elif diff >= 1:
        return "⚖️ Competitive"
    else:
        return "🎯 Target"

if not eligible_df.empty:
    eligible_df["Admission_Chance"] = eligible_df.apply(lambda r: assign_chance(r, user_aggregate), axis=1)

# --- QUICK METRICS DASHBOARD ---
m1, m2, m3 = st.columns(3)
m1.metric("🎯 Your Aggregate", f"{user_aggregate}")
m2.metric("✅ Qualified Courses", f"{len(eligible_df)}")
m3.metric("🏫 Matching Schools", f"{eligible_df['University'].nunique()}" if not eligible_df.empty else "0")

st.subheader("2️⃣ Your Results & AI Advisor Summary")

# --- CONVERSATIONAL ADVISOR SUMMARY ---
with st.container(border=True):
    st.markdown(f"### 💬 Advisor Response for Aggregate {user_aggregate}")
    if not eligible_df.empty:
        num_unis = eligible_df["University"].nunique()
        num_courses = len(eligible_df)
        
        st.write(
            f"Based on your **Aggregate {user_aggregate}**, you qualify for **{num_courses} programme(s)** "
            f"across **{num_unis} institution(s)** in your current search! **👉 Check Tab 2 below to lock in your Top 3 Choices & share via WhatsApp!**"
        )
        
        for uni, group in eligible_df.groupby("University"):
            course_list = [f"**{row['Course']}** *(Cut-off: {row['Cutoff']})*" for _, row in group.iterrows()]
            st.markdown(f"🏫 **{uni}:** You can offer {', '.join(course_list)}.")
    else:
        st.write(
            f"With **Aggregate {user_aggregate}**, none of the currently filtered
