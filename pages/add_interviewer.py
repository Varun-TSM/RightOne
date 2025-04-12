import streamlit as st
from db_manager import add_interviewer

st.title("➕ Add Interviewer Email")

with st.form("add_interviewer_form"):
    email = st.text_input("Enter Interviewer's Email Address")
    submitted = st.form_submit_button("Add Interviewer")

    if submitted:
        if email:
            add_interviewer(email)
            st.success(f"✅ Interviewer {email} added successfully!")
        else:
            st.error("⚠️ Please enter a valid email address.")

