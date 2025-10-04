import sqlite3

# 1. Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# 2. Create the users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT          -- "Admin", "Manager", or "Employee"
);
''')

# 3. Insert a sample Admin user for testing
try:
    c.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        ("Alice", "admin@test.com", "1234", "Admin")
    )
    conn.commit()
    print("✅ Database created and admin user added successfully.")
except sqlite3.IntegrityError:
    print("⚠️ Admin user already exists.")

conn.close()