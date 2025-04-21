import streamlit as st
import os
import sys
import glob
import json
import requests
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.app_info import show_notice_box
from modules.jd_parser import extract_jd_data 
from modules.resume_parser import extract_resume_data, SUPPORTED_EXTENSIONS
from db_manager import add_candidate
from sqlite_handler import (
    init_db, create_table, insert_resume,
    fetch_latest_resumes, is_resume_already_stored
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

def display_homepage():
    # ---------- Initialization ----------
    create_table()
    # Load Font Awesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .stFileUploader 
    {
        margin-top: 10px;
        padding: 40px 25px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid #e2e2e2;
    }
    .stAppHeader{ visibility: hidden;
    display:none;}
    .stButton>button{
        background-color: blue;  /* Blue background */
        color: white !important;            /* White text */
        padding: 10px 20px;      /* Small padding for compact size */
        font-size: 14px;         /* Smaller font size */
        border-radius: 15px;     /* Rounded corners for a cute look */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* Soft shadow for a soft look */
        display: inline-block;   /* Ensures it stays as a button */
        transition: all 0.3s ease;  /* Smooth transition for hover effect */
        border: none;            /* Remove any default border */
        text-decoration:none;
    }
    .stButton>button:hover {
        background-color: #0056b3; /* Darker blue on hover */
        transform: scale(1.1);      /* Slight scale on hover for a playful effect */
    }

    .stButton>button i {
        margin-right: 8px;  /* Add a small space between icon and text */
        font-size: 18px;    /* Slightly larger icon size */
    }
    /* Alert Wrapper - absolutely positioned */
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
    </style>""", unsafe_allow_html=True)
    
    st.markdown('<h1><i class="fas fa-robot"></i> rightOne - an HR assistant</h1>', unsafe_allow_html=True)
    st.write("")
    if "show_embedding_success" not in st.session_state:
        st.session_state.show_embedding_success = False

    # ---------- Main Layout ----------
    # Two-part split: Left for uploading resumes, right for job description input and results
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<h5><i class="fas fa-file-archive"></i> Step 1: Upload Resumes (ZIP)</h5>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["zip"])
        if uploaded_file and not st.session_state.get("resumes_parsed"):
            if st.button("Extract & Store Resumes"):
                with st.spinner("Processing resumes..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        response = requests.post("http://127.0.0.1:5000/upload", files=files)

                        if response.status_code == 200:
                            data = response.json()
                            save_path = data["save_path"]

                            resume_files = glob.glob(os.path.join(save_path, "**"), recursive=True)
                            resume_files = [
                                f for f in resume_files
                                if os.path.isfile(f) and os.path.splitext(f)[-1].lower() in SUPPORTED_EXTENSIONS
                            ]

                            for file_path in resume_files:
                                filename = os.path.basename(file_path)
                                if not is_resume_already_stored(filename):
                                    parsed_data = extract_resume_data(file_path)
                                    insert_resume(filename, parsed_data)

                            st.success("All resumes parsed and stored successfully.")
                            st.session_state.resumes_parsed = True  # ✅ Set flag here
                        else:
                            st.error(f"Backend Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")


    with col2:
        # JD Text Input
        st.markdown('<h5><i class="fas fa-file-signature"></i> Step 2: Paste Job Description</h5>', unsafe_allow_html=True)
        jd_text = st.text_area("", height=200, placeholder="e.g. We're hiring a data scientist...")
        if jd_text and not st.session_state.get("jd_parsed"):  # ⛔ Show only if not already parsed
            if st.button('Parse JD'):
                with st.spinner("Parsing JD..."):
                    placeholder = st.empty()
                    try:
                        jd_result = extract_jd_data(jd_text)
                        if jd_result:
                            st.success("JD parsed successfully!")
                            st.session_state.jd_parsed = True  # ✅ Mark as completed
                            placeholder.empty()

                            jd_result['required_skills'] = ', '.join(jd_result['required_skills'])
                            jd_df = pd.DataFrame([jd_result])
                            jd_df.to_excel("job_description.xlsx", index=False)
                        else:
                            st.error("Failed to parse JD.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ---------- View Parsed Resumes ----------
    stored_df = fetch_latest_resumes(limit=None)
    if not stored_df.empty:
        stored_df.to_excel("resume_parsed.xlsx", index=False)
    
    # ---------- Embedding Preparation ----------
    parsed_df = None
    if not stored_df.empty:
        try:
            jd_df = pd.read_excel("job_description.xlsx") if os.path.exists("job_description.xlsx") else None
            parsed_dicts = stored_df["parsed_json"].apply(json.loads)
            parsed_df = pd.DataFrame(parsed_dicts.tolist())
            parsed_df["filename"] = stored_df["filename"].values

            parsed_df["skills"] = parsed_df["skills"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
            parsed_df["experience"] = pd.to_numeric(parsed_df.get("experience", 0), errors="coerce").fillna(0).astype(int)
            parsed_df["Intern_Experience"] = pd.to_numeric(parsed_df.get("Intern_Experience", 0), errors="coerce").fillna(0).astype(int)
            parsed_df["graduation_year"] = parsed_df.get("graduation_year", "").astype(str)
            parsed_df["college"] = parsed_df.get("college", "")
            parsed_df["combined_text"] = parsed_df.apply(
                lambda row: f"{row['skills']} {row['experience']} {row['Intern_Experience']} {row['graduation_year']} {row['college']}",
                axis=1
            )
            if st.session_state.show_embedding_success:
                st.success(f"{len(parsed_df)} resumes ready for embedding.")
        except Exception as e:
            st.error(f"Error preparing resumes: {e}")

    if jd_df is not None:
        try:
            jd_df["combined_text"] = jd_df.apply(lambda row: " ".join(str(x) for x in row if pd.notna(x)), axis=1)
        except Exception as e:
            st.error(f"Error processing JD: {e}")
    else:
        st.warning("No JD Excel found.")

    if st.session_state.get("resumes_parsed") and st.session_state.get("jd_parsed"):

        def get_top_matching_resumes(df: pd.DataFrame, jd_text: str, threshold: float = 0.3, top_n: int = 10):
            df["combined_text"] = df["combined_text"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
            embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            jd_vector = np.array(embedding_model.embed_documents([jd_text])[0]).reshape(1, -1)
            resume_vectors = np.array(embedding_model.embed_documents(df["combined_text"].tolist()))
            similarities = cosine_similarity(jd_vector, resume_vectors)[0]
            df["similarity_score"] = similarities
            return df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False).head(top_n)

        if parsed_df is not None and jd_df is not None:
            if st.button("Get Top Matching Resumes"):
                with st.spinner("Matching resumes..."):
                    try:
                        top_matches = get_top_matching_resumes(parsed_df, jd_df["combined_text"].iloc[0])
                        if top_matches.empty:
                            st.warning("No suitable matches found.")
                        else:
                            st.success("Top matches retrieved!")
                            # Store top matching resumes in the database
                            for _, row in top_matches.iterrows():
                                name = row.get("name", "")
                                phone = row.get("phone", "")
                                email = row.get("email", "")
                                if email:  # Ensure email is present
                                    add_candidate(name, phone, email)

                            st.info("Top matching candidates added to the database.")
                            # Optionally, save the results to an Excel file
                            output_excel = "top_resume_matches_full_details.xlsx"
                            top_matches.to_excel(output_excel, index=False)
                            st.download_button(
                                label="Top Matching Resumes",
                                data=open(output_excel, "rb").read(),
                                file_name="top_resume_matches_full_details.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        st.error(f"Error during matching: {e}")

    # app information
    show_notice_box()



