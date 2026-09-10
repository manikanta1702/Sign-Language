from flask import Flask, render_template, request, redirect
import subprocess
import sys
import os
import sqlite3

from database import init_db, add_default_users, check_login, add_user

app = Flask(__name__)

# Initialize database
init_db()
add_default_users()

BASE_DIR = os.path.dirname(__file__)

# ===== LOGIN PAGE =====
@app.route('/')
def login():
    return render_template("login.html")


# ===== SIGNUP PAGE =====
@app.route('/signup')
def signup():
    return render_template("signup.html")


# ===== REGISTER USER =====
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    add_user(username, password)

    return redirect('/')


# ===== LOGIN CHECK =====
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = check_login(username, password)

        if user:
            if user[3] == "admin":
                return redirect("/admin")
            return render_template("select_mode.html")
        return "Invalid Username or Password"

    return render_template("select_mode.html")


# ===== ADMIN DASHBOARD =====
@app.route('/admin')
def admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT username, predicted_sign, timestamp FROM logs")
    logs = cursor.fetchall()

    conn.close()

    return render_template("admin.html", users=users, logs=logs)


# ===== RUN MODEL =====
@app.route('/run', methods=['POST'])
def run():
    mode = request.form.get("mode")

    asl_script = os.path.join(BASE_DIR, "..", "app", "realtime_asl.py")
    isl_script = os.path.join(BASE_DIR, "..", "app", "realtime_isl.py")

    if mode == "US":
        subprocess.Popen([sys.executable, asl_script])

    elif mode == "INDIA":
        subprocess.Popen([sys.executable, isl_script])

    return "Camera Started!"


if __name__ == '__main__':
    app.run(debug=True)
