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
        no_match_text = (
            f"With **Aggregate {user_aggregate}**, none of the currently filtered programmes match your cut-off threshold yet. "
            "Check the detailed guide below to see how close you are and what options to explore next!"
        )
        st.write(no_match_text)

# --- TABS SETUP ---
tab1, tab2, tab3, tab4 = st.tabs([
    f"✅ Qualified Cards ({len(eligible_df)})",
    "📂 Top 3 Choices & Share 🚀",
    f"📋 All Cut-Offs ({len(filtered_df)})",
    "⚖️ Compare"
])

with tab1:
    if not eligible_df.empty:
        st.write("Tap any course below to check its admission outlook and career path:")
        
        for _, row in eligible_df.iterrows():
            with st.expander(f"{row['University']} — {row['Course']} (Cut-off: {row['Cutoff']})"):
                st.markdown(f"**Field of Study:** {row['Category']}")
                st.markdown(f"**Admission Outlook:** **{row['Admission_Chance']}**")
                st.markdown(f"**Career Pathways:** {get_career_path(row['Course'])}")
        
        st.markdown("---")
        csv_data = eligible_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Qualified Courses (CSV)",
            data=csv_data,
            file_name=f"wassce_eligible_aggregate_{user_aggregate}.csv",
            mime="text/csv",
            key="download_qualified_csv_btn"
        )
    else:
        st.warning(f"### Why aren't any courses showing for Aggregate {user_aggregate}?")
        if filtered_df.empty:
            st.info(
                f"🔍 **No programmes matched your search or filter combination** "
                f"(*University: {selected_uni}*, *Field: {selected_cat}*, *Search: '{search_query}'*).\n\n"
                "**How to fix this:** Clear the search bar or switch both dropdowns back to **'All Universities'** and **'All Fields'**."
            )
        else:
            best_cutoff_here = int(filtered_df["Cutoff"].max())
            closest_courses = filtered_df[filtered_df["Cutoff"] == best_cutoff_here]["Course"].tolist()
            st.info(
                f"📊 **How WASSCE Cut-Offs Work:** In WASSCE grading, **lower numbers mean stronger grades** "
                f"(Aggregate 6 is the highest score, while 36 is the lowest). To qualify, your aggregate must be "
                f"**equal to or lower than** a programme's cut-off point.\n\n"
                f"For your current selection, the most flexible cut-off available is **Aggregate {best_cutoff_here}** "
                f"(for *{', '.join(closest_courses[:2])}*)—meaning your score of **{user_aggregate}** is currently "
                f"**{user_aggregate - best_cutoff_here} point(s) above** that threshold."
            )

with tab2:
    st.subheader("📂 Virtual Top 3 Admission Choices Planner & WhatsApp Share")
    st.write("Build your mock Ghanaian university application list and share your choices instantly!")
    
    if not eligible_df.empty:
        df_choices = df.copy()
        df_choices["Full_Choice"] = df_choices["University"] + " — " + df_choices["Course"] + " (Cut-off: " + df_choices["Cutoff"].astype(str) + ")"
        choice_options = df_choices["Full_Choice"].tolist()
        
        selected_choices = st.multiselect(
            "Select up to 3 choices for your application simulation",
            options=choice_options,
            max_selections=3,
            key="top_three_choices_planner"
        )
        
        if selected_choices:
            st.markdown("### 📋 Your Mock Application Summary:")
            summary_lines = [f"*My 2027 WASSCE Admission Plan (Aggregate {user_aggregate})*"]
            for i, choice in enumerate(selected_choices, 1):
                st.markdown(f"**Choice {i}:** {choice}")
                summary_lines.append(f"Choice {i}: {choice}")
            
            # WhatsApp Share Integration
            share_text = "\n".join(summary_lines)
            encoded_text = urllib.parse.quote(share_text)
            whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
            
            st.markdown(
                f'<br><a href="{whatsapp_url}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">'
                f'💬 Share My Top 3 Choices via WhatsApp</button></a><br><br>',
                unsafe_allow_html=True
            )
            
            if len(selected_choices) == 3:
                st.success("🎉 Excellent! You have filled all 3 choice slots for your simulation.")
                st.markdown("""
                **💡 Strategy Audit:**
                * Make sure your **1st Choice** is your dream course.
                * Ensure your **2nd or 3rd Choice** includes a safer cut-off to guarantee placement.
                """)
            else:
                st.info(f"You have selected {len(selected_choices)}/3 choices. Add up to 3 to complete your mock application portfolio.")
        else:
            st.info("💡 Choose up to 3 courses from the dropdown above to simulate your official university choices and unlock the WhatsApp share button.")
    else:
        st.warning("No eligible courses available with your current aggregate to populate choices.")

with tab3:
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

with tab4:
    st.write("Select programmes below to compare their cut-off points side-by-side:")
    if not filtered_df.empty:
        filtered_df["Display_Label"] = filtered_df["University"] + " - " + filtered_df["Course"]
        chosen_courses = st.multiselect(
            "Choose programmes to compare",
            options=filtered_df["Display_Label"].tolist(),
            max_selections=4,
            key="compare_courses_multiselect"
        )
        if chosen_courses:
            comparison_df = filtered_df[filtered_df["Display_Label"].isin(chosen_courses)]
            st.table(comparison_df[["University", "Category", "Course", "Cutoff"]])
        else:
            st.info("💡 Select up to 4 courses above to compare them side-by-side.")
    else:
        st.warning("No courses available to compare with current filters.")

# --- GENERAL ADMISSION GUIDELINES EXPANDER ---
st.markdown("---")
with st.expander("ℹ️ General Ghanaian University Admission Requirements (2027 Guide)"):
    st.markdown("""
    * **Core Subjects Rule:** Public universities require credit passes (**A1 to C6**) in Core English Language, Core Mathematics, and either Integrated Science or Social Studies.
    * **Elective Subjects:** You need credit passes in **3 elective subjects** relevant to your desired course of study.
    * **Competitive Cut-offs:** Highly competitive programmes like Medicine, Law, and Computer Engineering often require stricter thresholds (lower aggregates like 6 to 8).
    """)

# --- FOOTER ---
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 13px; margin-top: 24px;'>"
    "Built by Pendyn • Always verify final cut-offs against official 2027 university admission brochures."
    "</div>",
    unsafe_allow_html=True
)
