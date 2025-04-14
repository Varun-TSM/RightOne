# db/sqlite_handler.py
import sqlite3
import json
import os
from datetime import datetime
import pandas as pd

DB_FILE = "resumes.sqlite"

def init_db():
    """Initialize the database and create tables if they do not exist."""
    create_table()

def connect():
    return sqlite3.connect(DB_FILE)

def create_table():
    con = connect()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY,
            filename TEXT UNIQUE,
            parsed_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

def insert_resume(filename, parsed_data):
    con = connect()
    cur = con.cursor()

    # Get the next ID
    cur.execute("SELECT MAX(id) FROM resumes")
    result = cur.fetchone()
    next_id = (result[0] or 0) + 1

    cur.execute("""
        INSERT INTO resumes (id, filename, parsed_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        next_id,
        filename,
        json.dumps(parsed_data),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    con.commit()
    con.close()

def fetch_latest_resumes(limit=None):
    con = connect()
    cur = con.cursor()

    if limit is not None:
        cur.execute("""
            SELECT filename, parsed_json, created_at
            FROM resumes
            ORDER BY datetime(created_at) DESC
            LIMIT ?
        """, (limit,))
    else:
        cur.execute("""
            SELECT filename, parsed_json, created_at
            FROM resumes
            ORDER BY datetime(created_at) DESC
        """)

    rows = cur.fetchall()
    con.close()

    df = pd.DataFrame(rows, columns=["filename", "parsed_json", "created_at"])
    return df

def is_resume_already_stored(filename):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM resumes WHERE filename = ?", (filename,))
    result = cur.fetchone()[0]
    con.close()
    return result > 0
