import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WASSCE University Eligibility Checker",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Pendyn's University Checker")
st.write("Calculate your exact aggregate, check your university eligibility, and get instant admission recommendations for the 2027 cycle.")

@st.cache_data
def load_data():
    return pd.read_csv("cutoffs.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load cutoffs.csv. Error: {e}")
    st.stop()

# --- FEATURE 1: WASSCE GRADE CALCULATOR ---
with st.expander("📝 Need help finding your aggregate? Use the WASSCE Calculator"):
    st.write("Select your grades for your core subjects and best electives to automatically compute your aggregate.")
    
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
    
    st.info(f"✨ Calculated Best-6 Aggregate: **{calc_aggregate}**")

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

st.subheader("2️⃣ Your Results & AI Advisor Summary")

# --- NEW FEATURE: META-AI STYLE CONVERSATIONAL SUMMARY ---
with st.container(border=True):
    st.markdown(f"### 💬 Advisor Response for Aggregate {user_aggregate}")
    if not eligible_df.empty:
        num_unis = eligible_df["University"].nunique()
        num_courses = len(eligible_df)
        
        st.write(
            f"Based on your **Aggregate {user_aggregate}**, you qualify for **{num_courses} programme(s)** "
            f"across **{num_unis} institution(s)** in your current search! Here is a breakdown of where you can apply:"
        )
        
        # Group by university and write out clean conversational bullet points
        for uni, group in eligible_df.groupby("University"):
            course_list = [f"**{row['Course']}** *(Cut-off: {row['Cutoff']})*" for _, row in group.iterrows()]
            st.markdown(f"🏫 **{uni}:** You can offer {', '.join(course_list)}.")
    else:
        st.write(
            f"With **Aggregate {user_aggregate}**, none of the currently filtered programmes match your cut-off threshold yet. "
            "Check the detailed guide below to see how close you are and what options to explore next!"
        )

tab1, tab2, tab3 = st.tabs([
    f"✅ Qualified Table ({len(eligible_df)})",
    f"📋 All Listed Cut-Offs ({len(filtered_df)})",
    "⚖️ Compare Programmes"
])

with tab1:
    if not eligible_df.empty:
        st.dataframe(
            eligible_df[["University", "Course", "Category", "Cutoff"]],
            hide_index=True,
            width="stretch"
        )
        
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
            
            st.markdown("""
            **💡 What you can do next:**
            * **Broaden your search:** Switch University or Field of Study to **'All'**—another university may offer the same course with a higher cut-off.
            * **Check Tab 2 ('All Listed Cut-Offs'):** View the exact cut-off numbers for every listed programme so you can see how close you are.
            * **Explore alternative pathways:** Consider related programmes, fee-paying/diploma top-up routes, or resitting one or two subjects via **NOVDEC** to lower your aggregate.
            """)

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

with tab3:
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

# --- FEATURE 3: GENERAL ADMISSION GUIDELINES EXPANDER ---
st.markdown("---")
with st.expander("ℹ️ General Ghanaian University Admission Requirements (2027 Guide)"):
    st.markdown("""
    * **Core Subjects Rule:** Public universities require credit passes (**A1 to C6**) in Core English Language, Core Mathematics, and either Integrated Science or Social Studies.
    * **Elective Subjects:** You need credit passes in **3 elective subjects** relevant to your desired course of study.
    * **Competitive Cut-offs:** Highly competitive programmes like Medicine, Law, and Computer Engineering often require stricter thresholds (lower aggregates like 6 to 8).
    """)
