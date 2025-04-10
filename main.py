from flask import Flask, request, jsonify
import os
import zipfile
from datetime import datetime
import json
import numpy as np
import pandas as pd

from jd_parser import extract_jd_data
from resume_parser import extract_resume_data
from database.duckdb_handler import (
    create_table, insert_resume, fetch_latest_resumes,
    is_resume_already_stored
)
from embeddings import get_embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

SAVE_DIR = "extracted_resumes"
os.makedirs(SAVE_DIR, exist_ok=True)

# ----------------- 0. DB Setup -----------------
create_table()

# ----------------- 1. Upload ZIP Resumes -----------------
@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    zip_file = request.files['file']
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_path = os.path.join(SAVE_DIR, f"resumes_{timestamp}")
        os.makedirs(extract_path, exist_ok=True)

        zip_path = os.path.join(extract_path, 'resumes.zip')
        zip_file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        allowed_ext = ('.pdf', '.docx', '.doc', '.txt')
        resume_files = [
            os.path.join(root, f)
            for root, _, files in os.walk(extract_path)
            for f in files if f.lower().endswith(allowed_ext)
        ]

        return jsonify({
            "message": "✅ Resumes extracted and saved successfully.",
            "save_path": extract_path,
            "file_count": len(resume_files),
            "filenames": [os.path.basename(f) for f in resume_files]
        }), 200

    except zipfile.BadZipFile:
        return jsonify({"error": "❌ Invalid ZIP archive."}), 400
    except Exception as e:
        return jsonify({"error": f"❌ Something went wrong: {str(e)}"}), 500

# ----------------- 2. Parse JD -----------------
@app.route('/parse-jd', methods=['POST'])
def parse_jd():
    try:
        data = request.get_json()
        jd_text = data.get("jd_text")
        if not jd_text:
            return jsonify({"error": "❌ 'jd_text' is required."}), 400

        parsed_data = extract_jd_data(jd_text)

        if parsed_data:
            return jsonify({
                "message": "✅ JD parsed successfully.",
                "parsed_data": parsed_data
            }), 200
        else:
            return jsonify({"error": "❌ Failed to parse JD."}), 500

    except Exception as e:
        return jsonify({"error": f"❌ Error while parsing JD: {str(e)}"}), 500

# ----------------- 3. Store Parsed Resume -----------------
@app.route('/store-parsed-resume', methods=['POST'])
def store_parsed_resume():
    try:
        data = request.get_json()
        filename = data["filename"]
        resume_path = data["file_path"]

        if not is_resume_already_stored(filename):
            parsed_data = extract_resume_data(resume_path)
            insert_resume(filename, parsed_data)
            return jsonify({"message": "✅ Resume parsed and stored."}), 200
        else:
            return jsonify({"message": "ℹ️ Resume already exists."}), 200

    except Exception as e:
        return jsonify({"error": f"❌ Error storing resume: {str(e)}"}), 500

# ----------------- 4. Fetch Latest Resumes -----------------
@app.route('/fetch-latest-resumes', methods=['GET'])
def fetch_resumes():
    try:
        df = fetch_latest_resumes(limit=None)
        return df.to_json(orient="records"), 200
    except Exception as e:
        return jsonify({"error": f"❌ Could not fetch resumes: {str(e)}"}), 500

# ----------------- 5. Check if Resume Exists -----------------
@app.route('/check-resume-exists', methods=['POST'])
def check_resume_exists():
    try:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "❌ 'filename' is required."}), 400

        exists = is_resume_already_stored(filename)
        return jsonify({"exists": exists}), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error checking resume: {str(e)}"}), 500

# ----------------- 6. Get Top Matching Resumes -----------------
@app.route('/get-top-matches', methods=['POST'])
def get_top_matches():
    try:
        data = request.get_json()
        jd_text = data["jd_text"]
        resumes = data["resumes"]  # List of parsed resume dicts

        df = pd.DataFrame(resumes)
        df["combined_text"] = df.apply(
            lambda row: f"{row.get('skills', '')} {row.get('experience', '')} "
                        f"{row.get('Intern_Experience', '')} {row.get('graduation_year', '')} "
                        f"{row.get('college', '')}", axis=1
        )

        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        jd_vector = np.array(embedding_model.embed_documents([jd_text])[0]).reshape(1, -1)
        resume_vectors = np.array(embedding_model.embed_documents(df["combined_text"].tolist()))

        similarities = cosine_similarity(jd_vector, resume_vectors)[0]
        df["similarity_score"] = similarities

        top_matches = df[df["similarity_score"] > 0.3].sort_values(by="similarity_score", ascending=False).head(10)
        return top_matches[["filename", "similarity_score"]].to_json(orient="records"), 200

    except Exception as e:
        return jsonify({"error": f"❌ Matching error: {str(e)}"}), 500

# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(port=5000)
