import streamlit as st
from db_manager import add_interviewer
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.interviewer_email import send_availability_email

st.title("➕ Add Interviewer Email")

with st.form("add_interviewer_form"):
    email = st.text_input("Enter Interviewer's Email Address")
    submitted = st.form_submit_button("Add Interviewer")

    if submitted:
        if email:
            added = add_interviewer(email)
            if added:
                st.success(f"✅ Interviewer {email} added successfully!")
                
                if st.button("Send Invitation Email"):
                    send_availability_email(email)
                    
                    st.success(f"Invitation email sent to {email} successfully!")
                    
            else:
                st.info(f"ℹ️ Interviewer {email} is already in the database.")
        else:
            st.error("⚠️ Please enter a valid email address.")


