import json
import re
from langchain_groq import ChatGroq
import time
def extract_jd_data(jd_text, max_retries=3):
    """
    Extracts structured data from a single job description using Groq API.

    Args:
        jd_text (str): The job description text.
        max_retries (int): Maximum retries for API call.

    Returns:
        dict: Extracted data in structured JSON format.
    """
    llm = ChatGroq(
        temperature=0,
        groq_api_key="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",
        model_name="llama-3.1-8b-instant"
    )

    prompt = f"""
    You're an expert HR assistant. Extract the following details from the job description below
    and return the output strictly in valid JSON format:

    {{
        "job_title": <Extracted Job Title or null>,
        "Degree & Basic qualifications": <Extracted Degree or any>,
        "Location":<Extracted Location or null>,
        "experience_required": <Experience Required (in years or months) or make it 0>,
        "required_skills": <List of Technical Skills or null>,
        "job_type": <Full-time/Part-time/Contract/Internship or null>,
        "Company_name": <Extracted Company Name or null>,
    }}

    Do not include explanations. Only provide structured JSON.

    Job Description: {jd_text}
    """

    retries = 0
    while retries < max_retries:
        try:
            response = llm.invoke(prompt).content.strip()
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return None
        except Exception as e:
            print(f"Error on attempt {retries + 1}: {e}")
            time.sleep(2 ** retries)
            retries += 1

    print("Failed to extract JD data after maximum retries.")
    return None