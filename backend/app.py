from flask import Flask, render_template, request, redirect
import subprocess
import sys
import os
import sqlite3
import time
import json
import numpy as np

from database import init_db, add_default_users, check_login, add_user

app = Flask(__name__)

# Initialize database
init_db()
add_default_users()

BASE_DIR = os.path.dirname(__file__)
LATEST_PREDICTION_PATH = os.path.join(BASE_DIR, "latest_prediction.json")
TRANSLATOR_COMMAND_PATH = os.path.join(BASE_DIR, "translator_command.json")
translator_process = None
model_cache = {}
browser_sentences = {"ASL": [], "ISL": []}
browser_last_prediction = {"ASL": "", "ISL": ""}
browser_stable_count = {"ASL": 0, "ISL": 0}

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
            return render_template("home.html")
        return "Invalid Username or Password"

    return render_template("home.html")


# ===== PROFILE PAGE =====
@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/latest_prediction')
def latest_prediction():
    if not os.path.exists(LATEST_PREDICTION_PATH):
        return {"prediction": "", "language": ""}

    try:
        with open(LATEST_PREDICTION_PATH, "r", encoding="utf-8") as prediction_file:
            return json.load(prediction_file)
    except (OSError, json.JSONDecodeError):
        return {"prediction": "", "language": ""}


@app.route('/translator_space', methods=['POST'])
def translator_space():
    language = request.get_json(silent=True) or {}
    language = language.get("language", "ASL")
    if language not in browser_sentences:
        language = "ASL"
    browser_sentences[language].append(" ")
    try:
        write_prediction_state("SPACE", language)
        return {"sentence": "".join(browser_sentences[language])}
    except OSError:
        return "Could not add a space.", 500


def write_prediction_state(prediction, language):
    with open(LATEST_PREDICTION_PATH, "w", encoding="utf-8") as prediction_file:
        json.dump({
            "prediction": prediction,
            "sentence": "".join(browser_sentences[language]),
            "language": language,
        }, prediction_file)


def load_model_for_language(language):
    if language not in model_cache:
        import pickle
        import tensorflow as tf
        model_path = os.path.join(BASE_DIR, "..", "model", f"{language.lower()}_model.h5")
        encoder_path = os.path.join(BASE_DIR, "..", "model", f"{language.lower()}_label_encoder.pkl")
        with open(encoder_path, "rb") as encoder_file:
            encoder = pickle.load(encoder_file)
        model = tf.keras.models.load_model(model_path)
        model.predict(np.zeros((1, 63), dtype=np.float32), verbose=0)
        model_cache[language] = (model, encoder)
    return model_cache[language]


@app.route('/predict', methods=['POST'])
def predict():
    payload = request.get_json(silent=True) or {}
    language = "ASL" if payload.get("mode") == "US" else "ISL"
    landmarks = payload.get("landmarks")
    if not isinstance(landmarks, list) or len(landmarks) != 63:
        return {"error": "Expected 21 hand landmarks."}, 400

    try:
        model, encoder = load_model_for_language(language)
        values = np.array(landmarks, dtype=np.float32)
        if language == "ISL":
            max_value = np.max(np.abs(values))
            if max_value:
                values = values / max_value

        probabilities = model.predict(values.reshape(1, -1), verbose=0)[0]
        class_id = int(np.argmax(probabilities))
        confidence = float(probabilities[class_id])
        prediction = str(encoder.inverse_transform([class_id])[0])

        if prediction == browser_last_prediction[language]:
            browser_stable_count[language] += 1
        else:
            browser_last_prediction[language] = prediction
            browser_stable_count[language] = 1

        if confidence >= 0.55 and browser_stable_count[language] >= 3:
            if prediction == "SPACE":
                browser_sentences[language].append(" ")
            elif not browser_sentences[language] or browser_sentences[language][-1] != prediction:
                browser_sentences[language].append(prediction)
            browser_stable_count[language] = 0

        write_prediction_state(prediction, language)
        return {
            "prediction": prediction,
            "sentence": "".join(browser_sentences[language]),
            "confidence": confidence,
            "language": language,
        }
    except Exception as error:
        return {"error": str(error)}, 500


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
    global translator_process
    mode = request.form.get("mode")

    if mode not in {"US", "INDIA"}:
        return "Please select a valid sign language.", 400

    if translator_process and translator_process.poll() is None:
        translator_process.terminate()
        try:
            translator_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            translator_process.kill()

    if os.path.exists(LATEST_PREDICTION_PATH):
        os.remove(LATEST_PREDICTION_PATH)

    translator_process = None
    language = "ASL" if mode == "US" else "ISL"
    try:
        load_model_for_language(language)
    except Exception as error:
        return f"Translator model could not load: {error}", 500
    browser_sentences[language] = []
    browser_last_prediction[language] = ""
    browser_stable_count[language] = 0
    return "Camera and translator ready!"


if __name__ == '__main__':
    app.run(debug=True)
