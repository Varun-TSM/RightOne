# app.py
import streamlit as st
import os
import glob
import json
import requests
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jd_parser import extract_jd_data 
from resume_parser import extract_resume_data, SUPPORTED_EXTENSIONS
from db_manager import add_candidate
from sqlite_handler import (
    init_db, create_table, insert_resume,
    fetch_latest_resumes, is_resume_already_stored
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

# ---------- Initialization ----------
create_table()
st.set_page_config(page_title="rightOne - Resume Screener", layout="wide")

st.markdown("""<style>.stAppHeader { visibility: hidden; }</style>""", unsafe_allow_html=True)
st.title("🤖 rightOne - Resume Screening Assistant")

# ---------- Upload Resumes ----------
st.header("📥 Upload Resumes (ZIP)")

uploaded_file = st.file_uploader("Upload a ZIP file of resumes", type=["zip"])
if uploaded_file and st.button("📤 Extract & Store Resumes"):
    with st.spinner("Processing resumes..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post("http://127.0.0.1:5000/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                save_path = data["save_path"]
                st.success(data["message"])
                st.code(save_path)

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

                st.success("✅ All resumes parsed and stored successfully.")
            else:
                st.error(f"❌ Backend Error: {response.text}")
        except Exception as e:
            st.error(f"❌ Connection Error: {e}")

# ---------- Paste JD ----------
st.header("📝 Paste Job Description")
jd_text = st.text_area("Enter the job description below:", height=250, placeholder="e.g. We're hiring a data scientist...")

if jd_text and st.button("🔍 Parse JD"):
    with st.spinner("Parsing JD using ChatGroq..."):
        try:
            jd_result = extract_jd_data(jd_text)
            if jd_result:
                st.success("✅ JD parsed successfully!")
                st.subheader("📄 Parsed JD (JSON):")
                st.json(jd_result)

                jd_result['required_skills'] = ', '.join(jd_result['required_skills'])
                jd_df = pd.DataFrame([jd_result])
                jd_df.to_excel("job_description.xlsx", index=False)

                st.download_button(
                    label="📥 Download JD as Excel",
                    data=open("job_description.xlsx", "rb").read(),
                    file_name="job_description.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("❌ Failed to parse JD.")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------- View Parsed Resumes ----------
stored_df = fetch_latest_resumes(limit=None)
if not stored_df.empty:
    stored_df.to_excel("resume_parsed.xlsx", index=False)
    st.download_button(
        label="📥 Download All Parsed Resumes",
        data=open("resume_parsed.xlsx", "rb").read(),
        file_name="resume_parsed.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------- Embedding Preparation ----------
st.header("🔗 Prepare Embedding for Matching")

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
        st.success(f"✅ {len(parsed_df)} resumes ready for embedding.")
    except Exception as e:
        st.error(f"⚠️ Error preparing resumes: {e}")

if jd_df is not None:
    try:
        jd_df["combined_text"] = jd_df.apply(lambda row: " ".join(str(x) for x in row if pd.notna(x)), axis=1)
        st.success("✅ JD ready for embedding.")
    except Exception as e:
        st.error(f"⚠️ Error processing JD: {e}")
else:
    st.warning("⚠️ No JD Excel found.")

st.header("🏆 Resume Matching")

def get_top_matching_resumes(df: pd.DataFrame, jd_text: str, threshold: float = 0.3, top_n: int = 10):
    df["combined_text"] = df["combined_text"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    jd_vector = np.array(embedding_model.embed_documents([jd_text])[0]).reshape(1, -1)
    resume_vectors = np.array(embedding_model.embed_documents(df["combined_text"].tolist()))
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    df["similarity_score"] = similarities
    return df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False).head(top_n)

if parsed_df is not None and jd_df is not None:
    if st.button("🔍 Get Top Matching Resumes"):
        with st.spinner("Matching resumes..."):
            try:
                top_matches = get_top_matching_resumes(parsed_df, jd_df["combined_text"].iloc[0])
                if top_matches.empty:
                    st.warning("⚠️ No suitable matches found.")
                else:
                    st.success("✅ Top matches retrieved!")

                    # Store top matching resumes in the database
                    for _, row in top_matches.iterrows():
                        name = row.get("name", "")
                        phone = row.get("phone", "")
                        email = row.get("email", "")
                        if email:  # Ensure email is present
                            add_candidate(name, phone, email)

                    st.info("💾 Top matching candidates added to the database.")

                    # Optionally, save the results to an Excel file
                    output_excel = "top_resume_matches_full_details.xlsx"
                    top_matches.to_excel(output_excel, index=False)
                    st.download_button(
                        label="📥 Download Top Matching Resumes",
                        data=open(output_excel, "rb").read(),
                        file_name="top_resume_matches_full_details.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"❌ Error during matching: {e}")


# # ---------- Email Notification ----------
# st.header("✉️ Notify Interviewer via Email")
# interviewer_email = st.text_input("Interviewer Email", placeholder="e.g. recruiter@company.com")

# if interviewer_email and st.button("📧 Send Interview Slot Email"):
#     with st.spinner("Sending email..."):
#         try:
#             sender_email = "varunmayilvaganan11@gmail.com"
#             sender_password = "ykdx wymo kayk gxbi"
#             subject = "Interview Slot Selection"
#             body = """
#             Hello,

#             We are scheduling interviews. Kindly provide your available slots via the link below:

#             👉 http://localhost:8501/add_availability

#             Best regards,  
#             HR Team
#             """

#             msg = MIMEMultipart()
#             msg['From'] = sender_email
#             msg['To'] = interviewer_email
#             msg['Subject'] = subject
#             msg.attach(MIMEText(body, 'plain'))

#             server = smtplib.SMTP('smtp.gmail.com', 587)
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, interviewer_email, msg.as_string())
#             server.quit()

#             st.success("✅ Email sent successfully!")
#         except Exception as e:
#             st.error(f"❌ Failed to send email: {e}")
