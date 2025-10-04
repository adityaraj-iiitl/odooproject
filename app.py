# Make sure to import redirect and url_for!
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --- LOGIN FUNCTIONS (No changes here) ---
def get_user(email, password):
    # ... (this function stays the same)
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    return user

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    # ... (this function stays the same)
    email = request.form["email"]
    password = request.form["password"]
    user = get_user(email, password)
    if user:
        role = user["role"]
        name = user["name"]
        if role == "Admin":
            return f"<h2>✅ Welcome Admin, {name}!</h2>"
        else:
            return f"<h2>Welcome {name}!</h2>"
    else:
        return "<h2>❌ Invalid email or password. Please try again.</h2>"

# --- NEW SIGNUP FUNCTIONS ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # This block handles the form submission
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        
        # Use a try-except block to catch if the email already exists
        try:
            # Insert the new user with the role "Admin"
            c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                      (name, email, password, "Admin"))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "<h2>That email address is already in use. Please choose another.</h2>"
        
        conn.close()
        
        # After successful signup, redirect to the login page
        return redirect(url_for('home'))

    # This line handles showing the page initially (the GET request)
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)