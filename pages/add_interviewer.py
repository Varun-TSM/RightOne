import streamlit as st
from db_manager import add_interviewer, get_all_interviewers
from utils.interviewer_email import send_availability_email

st.title("➕ Add Interviewer Email")

with st.form("add_interviewer_form"):
    email = st.text_input("Enter Interviewer's Email Address")
    submitted = st.form_submit_button("Add Interviewer")

    if submitted:
        if email:
            added = add_interviewer(email)
            if added:
                send_availability_email(email)
                st.success(f"✅ Interviewer {email} added successfully and sent email!")
            else:
                st.info(f"ℹ️ Interviewer {email} is already in the database.")
        else:
            st.error("⚠️ Please enter a valid email address.")

# ⬇️ Display all interviewer emails from the database
st.subheader("📋 List of Interviewers")
interviewers = get_all_interviewers()

if interviewers:
    for i, interviewer_email in enumerate(interviewers, start=1):
        st.markdown(f"{i}. {interviewer_email}")
else:
    st.info("No interviewers found.")
