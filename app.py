from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

COUNTRY_CURRENCY_MAP = { "India": "INR", "United States": "USD", "United Kingdom": "GBP" }

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# --- DATABASE HELPER FUNCTIONS ---
def get_db_connection():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- AUTHENTICATION ROUTES ---
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['role'] = user['role']
        session['company_id'] = user['company_id']

        if session['role'] == "Admin":
            return redirect(url_for('dashboard'))
        else:
            return "<h2>Login successful! (Employee/Manager view coming soon)</h2>"
    else:
        flash("Invalid email or password.", "error")
        return redirect(url_for('home'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # ... (your signup code remains the same)
    return render_template("signup.html") # Simplified for brevity

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

# --- ADMIN DASHBOARD ROUTES ---
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('home'))

    conn = get_db_connection()
    # Get all users and their manager's name in one query using a LEFT JOIN
    users = conn.execute("""
        SELECT u.id, u.name, u.email, u.role, m.name as manager_name
        FROM users u
        LEFT JOIN users m ON u.manager_id = m.id
        WHERE u.company_id = ?
    """, (session['company_id'],)).fetchall()
    
    # Get a list of users who are managers to populate the dropdown
    managers = conn.execute("SELECT * FROM users WHERE role = 'Manager' AND company_id = ?", (session['company_id'],)).fetchall()
    conn.close()

    return render_template("dashboard.html", users=users, managers=managers)

@app.route("/add_user", methods=["POST"])
def add_user():
    # ... (this function is now updated with the password generator as shown above)
    return redirect(url_for('dashboard'))

@app.route("/assign_manager", methods=["POST"])
def assign_manager():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('home'))
        
    employee_id = request.form["employee_id"]
    manager_id = request.form["manager_id"]

    conn = get_db_connection()
    conn.execute("UPDATE users SET manager_id = ? WHERE id = ?", (manager_id, employee_id))
    conn.commit()
    conn.close()

    flash("Manager assigned successfully.", "success")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)