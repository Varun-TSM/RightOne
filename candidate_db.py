import sqlite3

# Connect to SQLite DB (or create it if it doesn't exist)
conn = sqlite3.connect("candidates.db")
cursor = conn.cursor()

# Step 1: Create the candidates table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'Pending'
    )
""")

# Step 2: Dummy data to insert
dummy_candidates = [
    ("John Doe", "123-456-7890", "john.doe@company.com", "Pending"),
    ("Jane Smith", "987-654-3210", "jane.smith@company.com", "Pending"),
    ("Alice Johnson", "555-555-5555", "alice.johnson@company.com", "Pending"),
    ("Bob Lee", "222-333-4444", "bob.lee@company.com", "Pending"),
    ("Varun", "+916383036342", "216107.varun.cse@cahcet.edu.in", "Pending"),
    ("Aditi", "555-555-556", "aditish2307@gmail.com", "Pending")
]

# Step 3: Insert data
for name, phone, email, status in dummy_candidates:
    try:
        cursor.execute("INSERT INTO candidates (name, phone, email, status) VALUES (?, ?, ?, ?)",
                       (name, phone, email, status))
    except sqlite3.IntegrityError:
        print(f"⚠️ Email already exists: {email}")

# Step 4: Commit and close
conn.commit()
conn.close()

print("✅ Table created and dummy data inserted.")
