from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# This function checks the database for a matching user
def get_user(email, password):
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row # This allows you to access columns by name
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    return user

# Route 1: The Home Page (/)
# This serves the login.html page when someone visits your website
@app.route("/")
def home():
    return render_template("login.html")

# Route 2: The Login Handler (/login)
# This handles the data when the login form is submitted
@app.route("/login", methods=["POST"])
def login():
    # Get form data
    email = request.form["email"]
    password = request.form["password"]

    # Check the database
    user = get_user(email, password)

    if user:
        # If user exists, check their role
        role = user["role"]
        name = user["name"]
        if role == "Admin":
            return f"<h2>✅ Welcome Admin, {name}!</h2>"
        else:
            return f"<h2>Welcome {name}!</h2>" # For Employee/Manager later
    else:
        # If user doesn't exist
        return "<h2>❌ Invalid email or password. Please try again.</h2>"

# This line makes the app run
if __name__ == "__main__":
    app.run(debug=True)