import streamlit as st
import pandas as pd
import requests
import os
import glob
import json
import numpy as np
from jd_parser import extract_jd_data 
from resume_parser import extract_resume_data, SUPPORTED_EXTENSIONS
from database.duckdb_handler import (
    create_table, insert_resume,
    fetch_latest_resumes, is_resume_already_stored
)
from embeddings import get_embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

# --- Initialize DB ---
create_table()

st.set_page_config(page_title="RightOne - Resume parser and hiring automation", layout="wide")
st.markdown("""
    <style>
    .stAppHeader { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 RightOne - Resume parser and hiring automation")

# ------------------ Resume Upload ------------------
st.header("📥 Upload Resumes")

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

                st.success("✅ All resumes parsed and stored.")
            else:
                st.error(f"❌ Backend error: {response.text}")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")

# ------------------ JD Text Section ------------------
st.header("📝 Paste Job Description")

jd_text = st.text_area("Enter or paste the job description here:", height=250, placeholder="e.g. We're hiring a data scientist...")

if jd_text and st.button("🔍 Parse JD"):
    with st.spinner("Parsing JD using ChatGroq..."):
        try:
            jd_result = extract_jd_data(jd_text)
            if jd_result:
                st.success("✅ JD parsed successfully!")
                st.subheader("📄 Parsed Job Description (JSON):")
                st.json(jd_result)

                jd_result['required_skills'] = ', '.join(jd_result['required_skills'])
                jd_df = pd.DataFrame([jd_result])
                excel_path = "job_description.xlsx"
                jd_df.to_excel(excel_path, index=False)

                st.success("✅ JD saved to Excel.")
                st.download_button(
                    label="Download Job Description Excel",
                    data=open(excel_path, 'rb').read(),
                    file_name='job_description.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                st.error("❌ Could not parse JD.")
        except Exception as e:
            st.error(f"Error: {e}")

# ------------------ View Resumes ------------------
stored_df = fetch_latest_resumes(limit=None)

if not stored_df.empty:
    # Save as Excel silently
    stored_df.to_excel("resume_parsed.xlsx", index=False)

    # Only show the download button, not the resumes
    st.download_button(
        label="📥 Download Parsed Resumes Excel",
        data=open("resume_parsed.xlsx", "rb").read(),
        file_name="resume_parsed.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ------------------ Prepare for Embedding ------------------
st.header("🔗 Prepare for Embedding (Resumes + JD)")

parsed_df = None

def get_top_matching_resumes(df: pd.DataFrame, jd_text: str, threshold: float = 0.5, top_n: int = 10) -> pd.DataFrame:
    df["combined_text"] = df["combined_text"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    jd_vector = np.array(embedding_model.embed_documents([jd_text])[0]).reshape(1, -1)
    resume_vectors = np.array(embedding_model.embed_documents(df["combined_text"].tolist()))
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    df["similarity_score"] = similarities
    return df[df["similarity_score"] > threshold].sort_values(by="similarity_score", ascending=False).head(top_n)

if not stored_df.empty:
    try:
        if os.path.exists("job_description.xlsx"):
            jd_df = pd.read_excel("job_description.xlsx")

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

        st.success(f"✅ {len(parsed_df)} resumes prepared for embedding.")
    except Exception as e:
        st.error(f"⚠️ Error preparing resumes: {e}")

if os.path.exists("job_description.xlsx"):
    try:
        jd_df = pd.read_excel("job_description.xlsx")
        jd_df["combined_text"] = jd_df.apply(lambda row: " ".join(str(x) for x in row if pd.notna(x)), axis=1)
        st.success(f"✅ JD prepared for embedding.")
    except Exception as e:
        st.error(f"⚠️ Error processing JD: {e}")
else:
    st.warning("⚠️ No JD Excel file found.")

# ------------------ Embed and Show Top Matches ------------------
st.header("🏆 Resume Matching")

if parsed_df is not None and "combined_text" in parsed_df.columns and not jd_df.empty:
    if st.button("🔍 Get Top Matches"):
        with st.spinner("Calculating best resume matches based on JD..."):
            try:
                top_matches = get_top_matching_resumes(parsed_df, jd_df["combined_text"].iloc[0], threshold=0.30)

                if top_matches.empty:
                    st.warning("⚠️ No matching resumes found.")
                else:
                    st.success("✅ Top matching resumes retrieved!")

                    # Display the top matches
                    st.dataframe(top_matches[["filename", "similarity_score"]])

                    # Save top matches as Excel
                    output_excel = "top_resume_matches.xlsx"
                    top_matches[["filename", "similarity_score"]].to_excel(output_excel, index=False)

                    # Offer download button
                    with open(output_excel, "rb") as file:
                        st.download_button(
                            label="📥 Download Top Matching Resumes Excel",
                            data=file.read(),
                            file_name="top_resume_matches.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            except Exception as e:
                st.error(f"❌ Error during similarity computation: {e}")

