import streamlit as st
from pages.home import homePage
from pages.resume_screening import Resume_Screener
from pages.add_availability import add_availabilities
from pages.add_interviewer import add_interviewers
from pages.book_slots import book_slots
from pages.hr_panel import HrPanel
import base64

# Set page configuration
st.set_page_config(page_title="RightOne",layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)
# Function to encode image as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load your image and convert to base64
logo_base64 = get_base64_image("pages/logo.png")

# Page routing using query parameters
query_params = st.query_params
page_title = query_params.get("page", "Home")
page_map = {
    "Home": {"func": homePage},
    "Resume Screening": {"func": Resume_Screener},
    "Availability": {"func": add_availabilities},
    "Interviewer": {"func": add_interviewers},
    "Book Slots": {"func": book_slots},
    "HR Panel": {"func": HrPanel},
}
current_page = page_map.get(page_title, page_map["Home"])

# Inject top navbar with base64 image
navbar_html = f"""
    <style>
        .stButton>button{{
            background-color: blue;  /* Blue background */
            color: white !important;  /* White text */
            padding: 10px 20px;      /* Small padding for compact size */
            font-size: 14px;         /* Smaller font size */
            border-radius: 15px;     /* Rounded corners for a cute look */
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* Soft shadow for a soft look */
            display: inline-block;   /* Ensures it stays as a button */
            transition: all 0.3s ease;  /* Smooth transition for hover effect */
            border: none;            /* Remove any default border */
            text-decoration:none;
        }}
        .stButton>button:hover {{
            background-color: #0056b3; /* Darker blue on hover */
            transform: scale(1.1);      /* Slight scale on hover for a playful effect */
        }}

        .stButton>button i {{
            margin-right: 8px;  /* Add a small space between icon and text */
            font-size: 18px;    /* Slightly larger icon size */
        }}

        div.block-container {{
            padding-top: 1rem;
        }}

        .stAppHeader, .css-1d391kg {{
            display: none;
        }}

        .stAppHeader {{
            visibility: hidden;
        }}

        /* Navbar styles */
        .navbar-custom {{
            background-color: #1A2639;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            width: 100%;
            box-sizing: border-box;
            border-radius: 10px;
            margin-bottom: 1rem;
        }}

        .navbar-brand {{
            display: flex;
            align-items: center;
            color: white;
            text-decoration: none;
            font-size: 1.5rem;
        }}

        .navbar-brand img {{
            height: 40px;
            margin-right: 12px;
        }}

        .navbar-nav {{
            display: flex;
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .navbar-nav .nav-item {{
            margin-left: 20px;
        }}

        .navbar-nav .nav-link {{
            color: white;
            text-decoration: none;
            font-size: 1.1rem;
            padding: 6px 10px;
        }}

        .navbar-nav .nav-link:hover {{
            border-radius: 6px;
            background-color: #324567;
        }}

        /* Hide sidebar on desktop/laptop (width >= 1024px) */
        @media (min-width: 1024px) {{
            .st-emotion-cache-i0ptax {{
                display: none !important;
            }}
        }}

        /* Show sidebar on mobile and tablet (width < 1024px) */
        @media (max-width: 1023px) {{
            .st-emotion-cache-1f3w014 {{
                display: block !important; /* Or flex, depending on layout */
            }}
        }}

        /* Hide sidebar on desktop/laptop */
        @media (min-width: 768px) {{
            .main {{
                margin-left: 0 !important;
            }}

            [data-testid="stSidebar"] {{
                display: none !important;
            }}
        }}

        /* Show sidebar on mobile */
        @media (max-width: 767px) {{
            [data-testid="stSidebar"] {{
                display: block !important;
                width: 100% !important;
            }}

            [data-testid="stSidebarNav"] {{
                text-align: center;
            }}

            section.main > div {{
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }}
        }}
    </style>

    <nav class="navbar-custom">
        <a href="?page=Resume%20Screening" class="navbar-brand">
            <img src="data:logo/png;base64,{logo_base64}" alt="Logo" style="width: 100px; height:100px"/>
        </a>
        <ul class="navbar-nav">
            <li class="nav-item"><a href="?page=Home" class="nav-link">Home</a></li>
            <li class="nav-item"><a href="?page=Resume%20Screening" class="nav-link">Resume Screening</a></li>
            <li class="nav-item"><a href="?page=Interviewer" class="nav-link">Interviewers</a></li>
            <li class="nav-item"><a href="?page=Availability" class="nav-link">Availability</a></li>
            <li class="nav-item"><a href="?page=Book Slots" class="nav-link">Book slot</a></li>
            <li class="nav-item"><a href="?page=HR Panel" class="nav-link">HR Panel</a></li>
        </ul>
    </nav>
"""

st.markdown(navbar_html, unsafe_allow_html=True)

# Render the page content
current_page["func"]()
