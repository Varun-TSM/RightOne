# db/duckdb_handler.py
import duckdb
import json, os
from datetime import datetime

DB_FILE = "resumes.duckdb"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

def connect():
    return duckdb.connect(DB_FILE)

def create_table():
    con = connect()
    con.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id BIGINT,
            filename TEXT UNIQUE,
            parsed_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.close()


def insert_resume(filename, parsed_data):
    con = connect()

    # Get the next ID
    result = con.execute("SELECT MAX(id) FROM resumes").fetchone()
    next_id = (result[0] or 0) + 1

    con.execute("""
        INSERT INTO resumes (id, filename, parsed_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        next_id,
        filename,
        json.dumps(parsed_data),
        datetime.now()
    ))
    con.close()


def fetch_latest_resumes(limit=None):
    con = connect()

    if limit is not None:
        df = con.execute("""
            SELECT filename, parsed_json, created_at
            FROM resumes
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).df()
    else:
        df = con.execute("""
            SELECT filename, parsed_json, created_at
            FROM resumes
            ORDER BY created_at DESC
        """).df()

    con.close()
    return df
def is_resume_already_stored(filename):
    con = connect()
    result = con.execute(
        "SELECT COUNT(*) FROM resumes WHERE filename = ?",
        (filename,)
    ).fetchone()[0]
    con.close()
    return result > 0


