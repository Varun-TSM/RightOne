import json
import random
import time
import pdfplumber
import os
from langchain_groq import ChatGroq
import textract
import subprocess
import docx2txt 
import docx2txt
from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_file_path):
    text = ""
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_file_path}: {e}")
        return None

    return text.strip() if text else None

def extract_text_from_docx(docx_file_path):
    text = ""
    try:
        text = docx2txt.process(docx_file_path)
    except Exception as e:
        print(f"Error reading {docx_file_path}: {e}")
        return None

    return text.strip() if text else None

def extract_text_from_scannedpdf(pdf_path):
    images = convert_from_path(pdf_path)

    # Apply OCR on each page
    extracted_text = "\n".join([pytesseract.image_to_string(img) for img in images])

    # Save extracted text to a file
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)

    return extracted_text
def is_scanned_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                return False # normal pdf
    return True  # scanned pdf
def extract_text_from_doc(file_path):
    try:
        text = textract.process(file_path).decode("utf-8")
        return text
    except Exception as e:
        print(f"Error extracting from .doc: {e}")
        return None



# List of your Groq API keys
GROQ_API_KEYS = [
    "API KEY 1",
    "API KEY 2",
    "API KEY 3",
    "API KEY 4"
]

def extract_first_json(text):
    """
    Extracts the first valid JSON object from a string that might contain extra content.
    """
    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(text)
        return obj
    except json.JSONDecodeError as e:
        print(f"JSON decode failed: {e}")
        return None

def query_groq_api(text, max_retries=3):
    # exponential back-off
    base_delay = 2
    # counts the tried
    retries = 0
    # track the keys used
    used_keys = set()

    while retries < max_retries and len(used_keys) < len(GROQ_API_KEYS):
        # Pick an unused API key
        available_keys = [k for k in GROQ_API_KEYS if k not in used_keys]
        api_key = random.choice(available_keys)
        used_keys.add(api_key)

        print(f"Using API Key: {api_key[-4:]} (rotated)")

        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="llama-3.1-8b-instant"
        )

        try:
            prompt = f"""
            You're an expert HR assistant. Extract the following details from the given resume text.
            Return output **strictly in this JSON format**:

            {{
              "name": "Full name of the candidate",
              "email": "Email address",
              "phone": "Contact number",
              "college": "Name of the college/university attended",
              "skills": ["skill1", "skill2", ...],
              "graduation_year": 2025,
              "certification": ["cert1", "cert2", ...],
              "experience": 0,
              "Intern_Experience": {{
                "duration_months": 0,
                "roles": ["role1", "role2", ...],
                "durations": ["2 months", "3 months"],
                "companies": ["Company A", "Company B"],
                "locations": ["onsite", "remote"]
              }}
            }}

            Guidelines:
            - If graduation year is 2025, then experience is 0.
            - If internships exist, calculate total duration in months.
            - If no internships, Intern_Experience should be null.
            - Reply strictly in JSON. No comments, no Markdown, no explanations.

            Resume Text:
            {text}
            """

            response = llm.invoke(prompt)
            raw_output = response.content.strip()

            parsed_response = extract_first_json(raw_output)
            if parsed_response:
                return parsed_response
            else:
                print("Could not extract JSON, trying next key...")

        except Exception as e:
            print(f"API error with key ending {api_key[-4:]}: {e}")
            wait_time = base_delay * (2 ** retries) + random.uniform(0, 1)
            print(f"Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            retries += 1

    print("Failed after exhausting all API keys or retries.")
    return None


SUPPORTED_EXTENSIONS = [".pdf", ".doc", ".docx"]

def convert_doc_to_pdf(input_path, output_dir="converted_pdfs"):
    os.makedirs(output_dir, exist_ok=True)
    try:
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_path
        ], check=True)
        output_pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
        return output_pdf_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting .doc to .pdf: {e}")
        return None

def extract_resume_data(file_path):
    file_extension = os.path.splitext(file_path)[-1].lower()

    # Skip unsupported file types
    if file_extension not in SUPPORTED_EXTENSIONS:
        print(f"Skipping unsupported file format: {file_extension} ({file_path})")
        return None

    # Convert .doc to .pdf
    if file_extension == ".doc":
        print(f"Converting .doc to .pdf: {file_path}")
        file_path = convert_doc_to_pdf(file_path)
        if not file_path:
            return None
        file_extension = ".pdf"

    # Extract text
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
        if not text or not text.strip():  # Check for non-scannable PDF
            print(f"No extractable text found in {file_path}, trying OCR...")
            text = extract_text_from_scannedpdf(file_path)
    elif file_extension == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        return None  # This line is safe but redundant due to check above

    if not text:
        print(f"No extractable text found in {file_path}")
        return None

    resume_data = query_groq_api(text)
    if resume_data:
        resume_data['resume_link'] = file_path

    return resume_data



