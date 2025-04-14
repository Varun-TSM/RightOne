import duckdb
import json

def load_resume_texts_from_duckdb():
    con = duckdb.connect("resumes.duckdb")
    results = con.execute("SELECT filename, parsed_json FROM resumes").fetchall()

    texts = []
    filenames = []
    for filename, parsed_json in results:
        try:
            data = json.loads(parsed_json)
            combined_text = " ".join([str(v) for v in data.values() if v])  # Flatten to string
            texts.append(combined_text)
            filenames.append(filename)
        except Exception as e:
            print(f"Skipping {filename}: {e}")
    return filenames, texts
