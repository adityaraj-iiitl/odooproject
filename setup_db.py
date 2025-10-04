import sqlite3
import os

# Get the absolute path of the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Create the full path for the database file
db_path = os.path.join(script_dir, "expenses.db")

print(f"--- Database will be created at this exact path: {db_path} ---")

# Connect using the absolute path
conn = sqlite3.connect(db_path)
c = conn.cursor()

# (Your companies table code remains the same)
c.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, currency TEXT NOT NULL
);
''')

# (Your users table code remains the same)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT,
    role TEXT, company_id INTEGER, manager_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id),
    FOREIGN KEY(manager_id) REFERENCES users(id)
);
''')

# NEW: The table for storing expense claims
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    category TEXT,
    expense_date TEXT,
    status TEXT NOT NULL, -- Will be 'Pending', 'Approved', or 'Rejected'
    employee_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES users(id),
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
''')

print("✅ Database tables created successfully.")
conn.commit()
conn.close()