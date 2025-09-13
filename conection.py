import sqlite3
import datetime

# Connect (this will create the DB file if not exists)
conn = sqlite3.connect("loginentry.db")

# Create a table
conn.execute("""
CREATE TABLE IF NOT EXISTS login (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# Insert a sample user
conn.execute("INSERT INTO login (name, password) VALUES (?, ?)", ("admin", "1234"))
conn.commit()

# Fetch all users
rows = conn.execute("SELECT * FROM login").fetchall()
for row in rows:
    print(row)

conn.close()
