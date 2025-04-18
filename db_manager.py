import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = "database.db"

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    """Initialize the database with required tables."""
    create_tables()

# ──────────────────────── TABLE CREATION FUNCTIONS ──────────────────────── #

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    

    # Interviewers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviewers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    """)

    # Candidates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Timezones Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timezones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Availability Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interviewer_id INTEGER NOT NULL,
            available_date TEXT NOT NULL,
            available_start_time TEXT NOT NULL,
            available_end_time TEXT NOT NULL,
            timezone_id INTEGER,
            FOREIGN KEY (interviewer_id) REFERENCES interviewers(id),
            FOREIGN KEY (timezone_id) REFERENCES timezones(id)
        )
    """)

   # Bookings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER UNIQUE NOT NULL,
            interviewer_id INTEGER NOT NULL,
            slot_date TEXT NOT NULL,
            slot_time TEXT NOT NULL,
            timezone_id INTEGER,
            requested_date TEXT,
            requested_time TEXT,
            request_status TEXT DEFAULT 'None',
            email_sent_status TEXT DEFAULT 'Not Sent',
            reason TEXT,  
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (interviewer_id) REFERENCES interviewers(id),
            FOREIGN KEY (timezone_id) REFERENCES timezones(id)
        )
    """)
    
    

    conn.commit()
    conn.close()

# ──────────────────────── INTERVIEWER FUNCTIONS ──────────────────────── #

def get_all_interviewers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM interviewers")
    emails = [row[0] for row in cursor.fetchall()]
    conn.close()
    return emails

def add_interviewer(email):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if the interviewer already exists
    cursor.execute("SELECT * FROM interviewers WHERE email = ?", (email,))
    exists = cursor.fetchone()

    if exists:
        conn.close()
        return False  # Not added, already exists

    # If not exists, insert
    cursor.execute("INSERT INTO interviewers (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    return True  # Successfully added


def get_interviewer_id(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM interviewers WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ──────────────────────── CANDIDATE FUNCTIONS ──────────────────────── #

def add_candidate(name, phone, email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO candidates (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()
    conn.close()

def get_candidate_id(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM candidates WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


# ──────────────────────── AVAILABILITY FUNCTIONS ──────────────────────── #

def add_availability(interviewer_id, date, start_time, end_time, timezone_id=None):
    conn = connect_db()
    cursor = conn.cursor()

    # Ensure all values are stored as strings
    date = date.isoformat() if hasattr(date, "isoformat") else str(date)
    start_time = start_time.isoformat() if hasattr(start_time, "isoformat") else str(start_time)
    end_time = end_time.isoformat() if hasattr(end_time, "isoformat") else str(end_time)

    # Check for existing identical availability
    cursor.execute("""
        SELECT 1 FROM availability
        WHERE interviewer_id = ?
        AND available_date = ?
        AND available_start_time = ?
        AND available_end_time = ?
    """, (interviewer_id, date, start_time, end_time))

    if cursor.fetchone():
        conn.close()
        return False  # Already exists, do not insert

    # Insert new availability
    cursor.execute("""
        INSERT INTO availability (interviewer_id, available_date, available_start_time, available_end_time, timezone_id)
        VALUES (?, ?, ?, ?, ?)
    """, (interviewer_id, date, start_time, end_time, timezone_id))

    conn.commit()
    conn.close()
    return True  # Successfully added


def get_interviewer_availabilities(interviewer_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT available_date, available_start_time, available_end_time 
        FROM availability WHERE interviewer_id = ?
    """, (interviewer_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "available_date": row[0],
            "available_start_time": row[1],
            "available_end_time": row[2]
        } for row in rows
    ]

def get_all_availabilities():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.email, a.interviewer_id, a.available_date, a.available_start_time, a.available_end_time
        FROM availability a
        JOIN interviewers i ON i.id = a.interviewer_id
    """)
    results = cursor.fetchall()
    conn.close()
    return results

# ──────────────────────── BOOKING FUNCTIONS ──────────────────────── #

def is_slot_booked(interviewer_id, slot_date, slot_time):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM bookings 
        WHERE interviewer_id = ? AND slot_date = ? AND slot_time = ?
    """, (interviewer_id, slot_date, slot_time))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def book_slot(candidate_email, interviewer_email, slot_date, slot_time, timezone_name='UTC'):
    # Check if the candidate is already booked with this interviewer for this date
    if is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, slot_date):
        raise ValueError(f"Candidate {candidate_email} is already booked for an interview with {interviewer_email} on {slot_date}.")

    # Rest of the existing booking logic
    conn = connect_db()
    cursor = conn.cursor()

    candidate_id = get_candidate_id(candidate_email)
    if candidate_id is None:
        raise ValueError(f"Candidate with email {candidate_email} not found. Please add candidate before booking.")

    interviewer_id = get_interviewer_id(interviewer_email)
    if interviewer_id is None:
        raise ValueError(f"Interviewer with email {interviewer_email} not found.")

    cursor.execute("SELECT id FROM timezones WHERE name=?", (timezone_name,))
    tz = cursor.fetchone()
    if not tz:
        cursor.execute("INSERT INTO timezones (name) VALUES (?)", (timezone_name,))
        timezone_id = cursor.lastrowid
    else:
        timezone_id = tz[0]

    cursor.execute("""
        INSERT INTO bookings (candidate_id, interviewer_id, slot_date, slot_time, timezone_id)
        VALUES (?, ?, ?, ?, ?)
    """, (candidate_id, interviewer_id, slot_date, slot_time, timezone_id))

    conn.commit()
    conn.close()


def is_candidate_already_booked_for_interviewer(candidate_email, interviewer_email, slot_date):
    candidate_id = get_candidate_id(candidate_email)
    interviewer_id = get_interviewer_id(interviewer_email)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM bookings
        WHERE candidate_id = ? AND interviewer_id = ? AND slot_date = ?
    """, (candidate_id, interviewer_id, slot_date))

    result = cursor.fetchone()
    conn.close()
    return result is not None


def has_candidate_booked(candidate_email):
    candidate_id = get_candidate_id(candidate_email)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bookings WHERE candidate_id=?", (candidate_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_candidate_booking(candidate_email):
    candidate_id = get_candidate_id(candidate_email)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.slot_date, b.slot_time, t.name 
        FROM bookings b
        LEFT JOIN timezones t ON b.timezone_id = t.id
        WHERE b.candidate_id=?
    """, (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"slot_date": row[0], "slot_time": row[1], "timezone": row[2]}
    return None

def get_all_bookings():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, c.email, b.slot_date, b.slot_time, t.name, i.email, b.request_status, b.email_sent_status
        FROM bookings b
        JOIN candidates c ON c.id = b.candidate_id
        JOIN interviewers i ON i.id = b.interviewer_id
        LEFT JOIN timezones t ON t.id = b.timezone_id
    """)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "candidate_email": row[1],
            "slot_date": row[2],
            "slot_time": row[3],
            "timezone": row[4],
            "interviewer_email": row[5],
            "request_status": row[6],
            "email_sent_status": row[7]
        }
        for row in rows
    ]

def update_missing_timezones():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM timezones WHERE name='UTC'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO timezones (name) VALUES ('UTC')")
        timezone_id = cursor.lastrowid
    else:
        timezone_id = result[0]

    cursor.execute("UPDATE bookings SET timezone_id = ? WHERE timezone_id IS NULL", (timezone_id,))
    conn.commit()
    conn.close()

# ──────────────────────── RESCHEDULE FUNCTIONS ──────────────────────── #

# def submit_reschedule_request(candidate_email, new_date, new_time, reason):
#     candidate_id = get_candidate_id(candidate_email)
#     conn = connect_db()
#     cursor = conn.cursor()

#     cursor.execute("""
#         UPDATE bookings SET
#         requested_date = ?, requested_time = ?, request_status = 'Pending', reason = ?
#         WHERE candidate_id = ?
#     """, (new_date, new_time, reason, candidate_id))

#     conn.commit()
#     conn.close()
def submit_reschedule_request(candidate_email, new_date, new_time, reason):
    conn = connect_db()
    cursor = conn.cursor()

    candidate_id = get_candidate_id(candidate_email)
    if candidate_id:
        cursor.execute("""
            UPDATE bookings SET
                requested_date = ?, 
                requested_time = ?, 
                request_status = 'Pending', 
                reason = ?
            WHERE candidate_id = ?
        """, (new_date, new_time, reason, candidate_id))
        conn.commit()
    conn.close()



def get_all_reschedule_requests():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, c.email, b.slot_date, b.slot_time, b.requested_date, b.requested_time, b.request_status, b.reason
        FROM bookings b
        JOIN candidates c ON b.candidate_id = c.id
        WHERE b.request_status = 'Pending'
    """)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "candidate_email": row[1],
            "current_slot_date": row[2],
            "current_slot_time": row[3],
            "requested_date": row[4],
            "requested_time": row[5],
            "status": row[6],
            "reason": row[7]  # Adding the reason field
        }
        for row in rows
    ]



def update_reschedule_status(booking_id, status):
    conn = connect_db()
    cursor = conn.cursor()

    if status == 'Approved':
        # Update slot_date and slot_time with requested values
        cursor.execute("""
            UPDATE bookings
            SET slot_date = requested_date,
                slot_time = requested_time,
                request_status = 'Approved',
                email_sent_status = 'Not Sent'
            WHERE id = ?
        """, (booking_id,))
    else:
        # Only update the request_status
        cursor.execute("""
            UPDATE bookings
            SET request_status = ?
            WHERE id = ?
        """, (status, booking_id))

    conn.commit()
    conn.close()


def add_request_status_column():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Try adding the missing column
        cursor.execute("ALTER TABLE bookings ADD COLUMN request_status TEXT DEFAULT 'None';")
        conn.commit()
        print("Column 'request_status' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error adding column: {e}")
    finally:
        conn.close()

def get_reschedule_count(candidate_email):
    """Check how many times a candidate has requested rescheduling."""
    candidate_id = get_candidate_id(candidate_email)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM bookings
        WHERE candidate_id = ? AND request_status = 'Pending'
    """, (candidate_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0  # Return count of reschedule requests

def update_invite_status(booking_id, email_sent_status):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE bookings SET email_sent_status = ? WHERE id = ?", (email_sent_status, booking_id))
    conn.commit()
    conn.close()
    