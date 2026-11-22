import streamlit as st

# Page setup
st.set_page_config(page_title="Pendyn's University Checker", page_icon="🎓")

st.title("🎓 Pendyn's University Checker")
st.write("Check your WASSCE aggregate eligibility for top Ghanaian universities.")

# Course and university lists
science_courses = [
    "Medicine", "Computer Science", "Pharmacy", "Engineering", 
    "Nursing", "Midwifery", "Computer Engineering", "IT", 
    "Biochemistry", "Physician Assistant"
]
business_courses = [
    "Business", "Business Administration", "Accounting", "Marketing", 
    "Economics", "Banking and Finance", "Human Resource", "Procurement"
]
arts_courses = [
    "Law", "History", "English", "Political Science", "Psychology", 
    "Sociology", "Theatre Arts", "Journalism", "Education", "Languages"
]

all_universities = ["KNUST", "UG", "UCC", "UDS", "UEW", "UMaT", "UHAS"]
all_courses = sorted(science_courses + business_courses + arts_courses)

# Interactive User Inputs
university = st.selectbox("Which university do you want to go to?", all_universities)
aggregate_score = st.number_input("Enter your WASSCE aggregate:", min_value=6, max_value=54, value=12, step=1)
course = st.selectbox("Which course do you wish to offer?", all_courses)

# Check Eligibility Button
if st.button("Check Eligibility", type="primary"):
    st.info(f"Nice choice! Checking **{course}** at **{university}**...")
    
    if course in science_courses:
        if 6 <= aggregate_score <= 12:
            st.success(f"🎉 Congrats! You qualify for **{course}** at **{university}**.")
        else:
            st.error(f"Sorry, for **{course}**, you need an aggregate between 6 and 12 for Science at **{university}**.")
            
    elif course in business_courses:
        if 6 <= aggregate_score <= 18:
            st.success(f"🎉 Congrats! You qualify for **{course}** at **{university}**.")
        else:
            st.error(f"Sorry, for **{course}**, you need an aggregate between 6 and 18 for Business.")
            
    elif course in arts_courses:
        if 6 <= aggregate_score <= 24:
            st.success(f"🎉 Congrats! You qualify for **{course}** at **{university}**.")
        else:
            st.error(f"Sorry, for **{course}**, you need an aggregate between 6 and 24 for Arts.")
