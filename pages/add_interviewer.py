import streamlit as st
import re
from db_manager import add_interviewer, get_all_interviewers
from utils.interviewer_email import send_availability_email
def add_interviewers():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    button.st-emotion-cache-b0y9n5.em9zgd08
    {
    background-color: blue;
        color: white !important;            
        padding: 10px 20px;      
        font-size: 14px;         
        border-radius: 15px;   
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  
        display: inline-block;   
        transition: all 0.3s ease;  
        border: none;            
        text-decoration:none;
    }
    button.st-emotion-cache-b0y9n5.em9zgd08:hover{
        background-color: #0056b3;
        transform: scale(1.1); 
    }
    .interviewer-list-wrapper {
    margin-top: 1.5rem;
    }

    .interviewer-item {
    padding: 12px 16px;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    margin-bottom: 10px;
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.03);
    display: flex;
    align-items: center;
    font-size: 0.95rem;
    color: white;
    transition: all 0.2s ease;
    }

    .interviewer-item:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        background-color: #004c97;
    }

    .interviewer-number {
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        text-align: center;
        line-height: 28px;
        margin-right: 12px;
        font-size: 0.85rem;
    }
    .stAlertWrapper {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        pointer-events: none; /* Prevents interfering with clicks below */
    }
    .stAlertContainer {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #38ef7d, #11998e);
            color: #ffffff;
            padding: 10px 16px;
            font-size: 12px;
            border-radius: 10px;
            font-weight: bold;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: all 0.4s ease-in-out;
            animation: floatIn 0.5s ease-out;
            border: 2px solid #ffffff33;
            z-index: 9999;
        }
        /* Float in animation */
        @keyframes floatIn {
            0% {
                opacity: 0;
                transform: translateY(20px) scale(0.95);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        /* Fade out animation */
        @keyframes fadeOut {
            to {
                opacity: 0;
                transform: translateY(10px);
            }
        }
    
        .stForm {
            width: 100%;
        }

        @media (min-width: 768px) {
            .stForm {
                width: 50%;
            
            }
            .interviewer-item{
                width:40%;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style='font-weight:600;'>
        <i class="fas fa-user-plus" style="margin-right:10px; color:#007BFF;"></i>Add Interviewer Email
    </h3>
    """, unsafe_allow_html=True)

    with st.form("add_interviewer_form"):
        email = st.text_input("Enter Interviewer's Email Address")
        submitted = st.form_submit_button("Add Interviewer")

        if submitted:
            if email:
                # Validate email format and ensure it's a Gmail address
                if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
                    st.error("⚠️ Please enter a valid email address (e.g., example@gmail.com).")
                else:
                    added = add_interviewer(email)
                    if added:
                        send_availability_email(email)
                        st.success(f"✅ Interviewer {email} added successfully and sent email!")
                    else:
                        st.info(f"ℹ️ Interviewer {email} is already in the database.")
            else:
                st.error("⚠️ Email address is required.")

    st.markdown("""
    <h4 style='font-weight: 600; margin-top: 2rem;'>
        <i class="fas fa-address-book" style="color:#007BFF; margin-right: 8px;"></i> List of Interviewers
    </h4>
    """, unsafe_allow_html=True)
    interviewers = get_all_interviewers()

    st.markdown('<div class="interviewer-list-wrapper">', unsafe_allow_html=True)

    if interviewers:
        for i, interviewer_email in enumerate(interviewers, start=1):
            st.markdown(f'''
                <div class="interviewer-item">
                    <div class="interviewer-number">{i}</div>
                    {interviewer_email}
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No interviewers found.")

    st.markdown('</div>', unsafe_allow_html=True)
