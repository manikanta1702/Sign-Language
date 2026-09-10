import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pickle
import os
import sqlite3
import threading
import time

# ---------- PATHS ----------
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "gesture_model.h5")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "model", "label_encoder.pkl")

# ---------- PLACEHOLDERS (will be loaded in background) ----------
model = None
encoder = None
model_ready = False


def load_model_background():
    global model, encoder, model_ready, hands
    try:
        # load model + encoder
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(ENCODER_PATH, "rb") as f:
            encoder = pickle.load(f)

        # initialize mediapipe Hands after model is loaded
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        model_ready = True
    except Exception as e:
        print("Model load error:", e)
        model_ready = False

# ---------- DATABASE FUNCTION ----------
# Resolve database path relative to this file so it works
DB_PATH = os.path.join(BASE_DIR, "..", "backend", "database.db")

def save_log(prediction):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO logs (username, predicted_sign) VALUES (?, ?)",
            ("user", prediction)
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

# ---------- MEDIAPIPE ----------
mp_hands = mp.solutions.hands
hands = None
# drawing utils are lightweight
draw = mp.solutions.drawing_utils

# ---------- CAMERA ----------
# Open camera immediately so the UI shows frames while model loads
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(3, 640)
cap.set(4, 480)

# Start model loading in a background thread
loader_thread = threading.Thread(target=load_model_background, daemon=True)
loader_thread.start()

# Quick warm-up reads so the camera stream stabilizes
for _ in range(3):
    cap.read()

# ---------- SENTENCE LOGIC ----------
sentence = []
last_prediction = ""
stable_count = 0
STABLE_THRESHOLD = 12  # slightly faster response

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    gesture_text = ""

    # If model isn't ready yet, just show raw camera with loading indicator
    if not model_ready:
        cv2.putText(frame, "Loading model...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        # MEDIAPIPE processing (initialize once when model ready)
        try:
            # Ensure mediapipe objects exist (they were created earlier)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            result = hands.process(rgb)
            rgb.flags.writeable = True

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # ---------- FEATURE ENGINEERING ----------
                    landmarks = []
                    base_x = hand_landmarks.landmark[0].x
                    base_y = hand_landmarks.landmark[0].y

                    for lm in hand_landmarks.landmark:
                        landmarks.extend([
                            lm.x - base_x,
                            lm.y - base_y,
                            lm.z
                        ])

                    # Scale normalization
                    max_value = max(abs(x) for x in landmarks)
                    if max_value != 0:
                        landmarks = [x / max_value for x in landmarks]

                    X_input = np.array(landmarks).reshape(1, -1)

                    # ---------- PREDICTION ----------
                    prediction = model.predict(X_input, verbose=0)
                    class_id = np.argmax(prediction)
                    confidence = float(np.max(prediction))

                    gesture_text = encoder.inverse_transform([class_id])[0]

                    # ---------- STABILITY + CONFIDENCE ----------
                    if confidence > 0.75:
                        if gesture_text == last_prediction:
                            stable_count += 1
                        else:
                            stable_count = 0
                            last_prediction = gesture_text

                        if stable_count == STABLE_THRESHOLD:
                            if gesture_text == "SPACE":
                                sentence.append(" ")
                            else:
                                if len(sentence) == 0 or sentence[-1] != gesture_text:
                                    sentence.append(gesture_text)
                                    save_log(gesture_text)

                            stable_count = 0

                    # ---------- DISPLAY CURRENT GESTURE ----------
                    cv2.putText(
                        frame,
                        f"{gesture_text} ({confidence*100:.1f}%)",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0),
                        2
                    )
        except Exception as e:
            # If anything in processing fails, print error and continue showing frames
            print("Processing error:", e)

    # ---------- SUBTITLE BAR ----------
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, h - 60), (w, h), (255, 255, 255), -1)

    subtitle = "".join(sentence[-15:])
    cv2.putText(
        frame,
        subtitle,
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 0),
        2
    )

    cv2.imshow("Sign Language Translator (Advanced)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        sentence.clear()

cap.release()
cv2.destroyAllWindows()
