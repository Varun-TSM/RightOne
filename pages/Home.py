import streamlit as st
import pandas as pd
import numpy as np

from pages import resume_screening
from pages.resume_screening import Resume_Screener

def homePage():
    # Custom CSS for the entire application with theme compatibility
    st.markdown("""
   <style>
    /* Card styling with theme compatibility */
    .card {
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        height: 100%;
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid rgba(100, 100, 100, 0.2);
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.15);
    }

    .card-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: #4D96FF;
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: inherit;
    }

    .card-text {
        opacity: 0.85;
        color: inherit;
    }

    /* Section styling */
    .section {
        margin-bottom: 4rem;
    }

    .section-heading {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        text-align: center;
        color: inherit;
    }

    /* How It Works Section Styling */
        .how-it-works-container {
            display: flex;
            flex-direction: column;
            align-items: center; /* Center the content horizontally */
            justify-content: center; /* Center the content vertically (if needed) */
        }

        .how-it-works-step {
            width: 90%;
            max-width: 800px;
            display: flex;
            align-items: center;
            background-color: rgba(200, 200, 200, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid rgba(100, 100, 100, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            justify-content: center; /* Center the content inside each step */
        }


        .step-number {
            background-color: #4D96FF;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 1.5rem;
            flex-shrink: 0;
        }

        .step-content {
            flex-grow: 1;
        }

        .step-title {
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            color: inherit;
        }

        .step-description {
            opacity: 0.85;
            color: inherit;
        }

    /* Button styling */
    .cta-button {
        background-color: #4D96FF;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
        display: inline-block;
        text-align: center;
    }

    .cta-button:hover {
        background-color: #3A7BD5;
    }

    /* Footer styling */
   .footer {
    background-color: rgba(200, 200, 200, 0.1);
    padding: 2rem 1rem;
    border-radius: 10px;
    margin-top: 2rem;
    text-align: center;
    color: inherit;
    border: 1px solid rgba(100, 100, 100, 0.2);
    margin-bottom: 0;  /* Remove extra bottom margin */
    padding-bottom: 1rem;  /* Adjust bottom padding as needed */
    }


    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
    }

    .footer-link {
        color: #4D96FF;
        text-decoration: none;
    }

    .footer-link:hover {
        text-decoration: underline;
    }

    /* Hero section styling */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: inherit;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.85;
        margin-bottom: 2rem;
        max-width: 800px;
        color: inherit;
    }

    /* === UPDATED CARD GRID TO FIX ROW LAYOUT === */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        justify-items: center;
        margin-bottom: 3rem;
    }

    .card-wrapper {
        width: 100%;
        max-width: 350px;
    }

    /* 2 cards per row on medium screens */
    @media (max-width: 1024px) {
        .card-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    /* Stack cards on mobile */
    @media (max-width: 600px) {
        .card-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Main content width */
    .main .block-container {
        max-width: 1200px !important;
        margin: 0 auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Hide sidebar on desktop/laptop */
    @media (min-width: 768px) {
        [data-testid="stSidebar"] {
            display: none !important;
        }
        .main {
            margin-left: 0 !important;
        }
    }

    /* Show sidebar on mobile */
    @media (max-width: 767px) {
        [data-testid="stSidebar"] {
            display: block !important;
            width: 100% !important;
        }

        [data-testid="stSidebarNav"] {
            text-align: center;
        }

        section.main > div {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>

    """, unsafe_allow_html=True)


    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">AI-Powered Resume Screening & Interview Scheduling</h1>
        <p class="hero-subtitle">Simplify your hiring process with AI-driven resume matching, dynamic interview scheduling, and seamless rescheduling—all in one platform. Connect, evaluate, and manage interviews with ease.</p>
    </div>
    """, unsafe_allow_html=True)

    # Center the button using columns
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        # Button for demo
        if st.button("Try resume screener", key="hero_cta", use_container_width=True):
            # This would normally use switch_page, but now we'll just set a session state
            st.session_state['page'] = 'demo'
            st.rerun()

    # Feature Cards Section
    st.markdown('<h2 class="section-heading">Key Features</h2>', unsafe_allow_html=True)

    # Responsive Card Grid
    st.markdown("""
    <div class="card-grid">
        <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-users"></i></div>
                <h3 class="card-title">Top Matching Resumes</h3>
                <p class="card-text">Automatically rank resumes based on job fit for faster, more accurate hiring decisions.</p>
            </div>
        </div>
        
    <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-random"></i></div>
                <h3 class="card-title">Flexibility</h3>
                <p class="card-text">Enable dynamic, conflict-free interview scheduling with real-time availability.</p>
            </div>
        </div>
        
    <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-handshake"></i></div>
                <h3 class="card-title">HR Connect</h3>
                <p class="card-text"> Streamline candidate tracking and communication with a dedicated HR dashboard.</p>
            </div>
        </div>

    <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-sync-alt"></i></div>
                <h3 class="card-title">Reschedule Requests</h3>
                <p class="card-text">Effortlessly manage interview reschedules with quick approval workflows.</p>
            </div>
        </div>
        
    <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-calendar-alt"></i></div>
                <h3 class="card-title">Bookings List</h3>
                <p class="card-text">Get an overview of all interview bookings with detailed scheduling insights.</p>
            </div>
        </div>
    <div class="card-wrapper">
            <div class="card">
                <div class="card-icon"><i class="fas fa-bolt"></i></div>
                <h3 class="card-title">No Delays</h3>
                <p class="card-text">Keep candidates and interviewers informed with automated email notifications and reminders.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # How It Works Section
    st.markdown('<h2 class="section-heading">How It Works?</h2>', unsafe_allow_html=True)

    # Wrap the "How It Works" steps in a container for centering
    st.markdown('<div class="how-it-works-container" style = "margin-bottom: 3rem;">', unsafe_allow_html=True)

    steps = [
        {"number": 1, "title": "Upload Resumes & Job Description", 
        "description": "HR uploads a ZIP file containing resumes and the job description. The system automatically extracts the top matching resumes."},
        {"number": 2, "title": "Shortlisted Candidates in HR Connect", 
        "description": "The shortlisted candidates are displayed in the HR Connect panel, providing HR with easy access to the top candidates."},
        {"number": 3, "title": "Add Interviewers & Slot Availability", 
        "description": "HR adds interviewers to the system, and they receive an email requesting their availability for interview slots."},
        {"number": 4, "title": "Dynamic Candidate Slot Selection", 
        "description": "Candidates select interview slots based on interviewer's availability."},
        {"number": 5, "title": "Reschedule & Approval", 
        "description": "Candidates can reschedule, and HR approves the new slot."}
    ]

    for step in steps:
        st.markdown(f"""
        <div class="how-it-works-step" style="max-width: 800px; margin: 5px auto;">
            <div class="step-number">{step['number']}</div>
            <div class="step-content">
                <div class="step-title">{step['title']}</div>
                <div class="step-description">{step['description']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close the container

    # Call to Action
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0;">
        <h2 style="margin-bottom: 1rem;">Ready to transform your hiring process?</h2>
    </div>
    """, unsafe_allow_html=True)

     # Center the button using columns
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        # Button for demo
        if st.button("Book a Demo", key="bottom_cta", use_container_width=True):
            # This would normally use switch_page, but now we'll just set a session state
            st.session_state['page'] = 'demo'
            st.rerun()

    # Footer
    st.markdown("""
    <div class="footer">
        <div class="footer-links">
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">Terms of Service</a>
            <a href="#" class="footer-link">Contact Us</a>
            <a href="#" class="footer-link">About</a>
        </div>
        <div class="footer-copyright">
            © 2025 RightOne. All rights reserved.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Simple page navigation (alternative to streamlit-extras)
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'




