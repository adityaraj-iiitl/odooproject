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

# Find the @app.route("/signup"...) function in app.py and replace it with this

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # This block handles the form submission when the method is POST
    if request.method == "POST":
        company_name = request.form["company_name"]
        admin_name = request.form["name"]
        email = request.form["email"]
        country = request.form["country"]
        password = request.form["password"]

        currency = COUNTRY_CURRENCY_MAP.get(country, "USD")

        conn = get_db_connection()
        try:
            # Step 1: Create the new company
            cursor = conn.execute("INSERT INTO companies (name, currency) VALUES (?, ?)", (company_name, currency))
            company_id = cursor.lastrowid

            # Step 2: Create the new admin user
            conn.execute("INSERT INTO users (name, email, password, role, company_id) VALUES (?, ?, ?, ?, ?)",
                      (admin_name, email, password, "Admin", company_id))
            conn.commit()
        except sqlite3.IntegrityError:
            flash(f"Error: The email '{email}' already exists.", "error")
            conn.close()
            # If email exists, just show the signup page again with an error
            return redirect(url_for('signup'))
        finally:
            conn.close()

        # This is the crucial line for a successful signup
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('home'))

    # This line runs for a GET request to simply show the page
    return render_template("signup.html")

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