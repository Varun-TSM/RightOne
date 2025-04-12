import sqlite3

DB_FILE = "database.db"

def connect_db():
    conn = sqlite3.connect("DB_FILE")
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
            FOREIGN KEY (candidate_id) REFERENCES candidates(id),
            FOREIGN KEY (interviewer_id) REFERENCES interviewers(id),
            FOREIGN KEY (timezone_id) REFERENCES timezones(id)
        )
    """)

    conn.commit()
    conn.close()

# ──────────────────────── INTERVIEWER FUNCTIONS ──────────────────────── #

def add_interviewer(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO interviewers (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()

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
    cursor.execute("""
        INSERT INTO availability (interviewer_id, available_date, available_start_time, available_end_time, timezone_id)
        VALUES (?, ?, ?, ?, ?)
    """, (interviewer_id, date, start_time, end_time, timezone_id))
    conn.commit()
    conn.close()

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
    conn = connect_db()
    cursor = conn.cursor()

    candidate_id = get_candidate_id(candidate_email)
    interviewer_id = get_interviewer_id(interviewer_email)

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
        SELECT b.id, c.email, b.slot_date, b.slot_time, t.name, i.email, b.request_status
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
            "request_status": row[6]
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

def submit_reschedule_request(candidate_email, new_date, new_time):
    candidate_id = get_candidate_id(candidate_email)
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings SET
        requested_date = ?, requested_time = ?, request_status = 'Pending'
        WHERE candidate_id = ?
    """, (new_date, new_time, candidate_id))

    conn.commit()
    conn.close()

def get_all_reschedule_requests():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, c.email, b.slot_date, b.slot_time, b.requested_date, b.requested_time, b.request_status
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
            "status": row[6]
        }
        for row in rows
    ]

def update_reschedule_status(booking_id, status):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bookings SET request_status = ? WHERE id = ?
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

    
        
# ──────────────────────── MAIN ──────────────────────── #

if __name__ == "__main__":
    init_db()

