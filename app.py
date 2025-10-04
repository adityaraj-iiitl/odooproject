from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import string
import os # Add the os import

# Get the absolute path for the database, just like in the setup script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "expenses.db")

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# Update the helper function to use the absolute path
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

COUNTRY_CURRENCY_MAP = { "India": "INR", "United States": "USD", "United Kingdom": "GBP" }

# --- AUTHENTICATION ROUTES ---
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
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
            elif session['role'] == "Employee":
                return redirect(url_for('employee_dashboard'))
            elif session['role'] == "Manager":
                return "<h2>Manager Dashboard coming soon!</h2>"
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('home'))
    
    # This handles the GET request for the login page
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # ... (your full signup function)
    if request.method == "POST":
        # ... (full logic for signup POST)
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('home'))
    return render_template("signup.html")


# --- ADMIN DASHBOARD ROUTES ---
@app.route("/dashboard")
def dashboard():
    # ... (your full dashboard function)
    return "Admin dashboard placeholder" # Placeholder for brevity

@app.route("/add_user", methods=["POST"])
def add_user():
    # ... (your full add_user function)
    return "Add user placeholder" # Placeholder for brevity

@app.route("/assign_manager", methods=["POST"])
def assign_manager():
    # ... (your full assign_manager function)
    return "Assign manager placeholder" # Placeholder for brevity


# --- EMPLOYEE DASHBOARD ROUTES ---
@app.route("/employee_dashboard")
def employee_dashboard():
    if 'user_id' not in session or session['role'] not in ['Employee', 'Manager']:
        return redirect(url_for('home'))

    conn = get_db_connection()
    expenses = conn.execute(
        "SELECT * FROM expenses WHERE employee_id = ? ORDER BY expense_date DESC",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template("employee_dashboard.html", expenses=expenses)

@app.route("/submit_expense", methods=["POST"])
def submit_expense():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    description = request.form["description"]
    amount = request.form["amount"]
    currency = request.form["currency"]
    category = request.form["category"]
    expense_date = request.form["expense_date"]
    
    employee_id = session['user_id']
    company_id = session['company_id']

    conn = get_db_connection()
    conn.execute(
        """INSERT INTO expenses 
        (description, amount, currency, category, expense_date, status, employee_id, company_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (description, amount, currency, category, expense_date, "Pending", employee_id, company_id)
    )
    conn.commit()
    conn.close()

    flash("Expense claim submitted successfully!", "success")
    return redirect(url_for('employee_dashboard'))


if __name__ == "__main__":
    app.run(debug=True)