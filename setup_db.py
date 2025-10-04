import sqlite3
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# It must have the code for the companies table
c.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    currency TEXT NOT NULL
);
''')

# And the code for the updated users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
''')

print("✅ Database tables created successfully.")
conn.commit()
conn.close()