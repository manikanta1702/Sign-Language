import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import deque
import threading
import time

# ===== LOAD MODEL =====
# model may be heavy; load in background while opening camera
model = None
model_ready = False

# ===== MEDIAPIPE SETUP =====
mp_hands = mp.solutions.hands
hands = None

draw = mp.solutions.drawing_utils


def init_background():
    global model, model_ready, hands
    try:
        model = pickle.load(open("../model/model.pkl", "rb"))
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        model_ready = True
    except Exception as e:
        print("Init error:", e)

# ===== CAMERA SETUP =====
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
cap.set(cv2.CAP_PROP_CONTRAST, 50)
cap.set(3, 1280)
cap.set(4, 720)

# start background init
bg_thread = threading.Thread(target=init_background, daemon=True)
bg_thread.start()

# Warm-up
for _ in range(3):
    cap.read()

# ===== STABILITY SYSTEM =====
prediction_buffer = deque(maxlen=10)
stable_text = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # If not ready, show initializing text
    if not model_ready or hands is None:
        cv2.putText(frame, "Initializing...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    else:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = hands.process(rgb)
        rgb.flags.writeable = True

        if result.multi_hand_landmarks:
            left_hand = [0] * 63
            right_hand = [0] * 63

            for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
                hand_label = result.multi_handedness[idx].classification[0].label

                temp = []

                # ===== FEATURE ENGINEERING =====
                base_x = hand_landmarks.landmark[0].x
                base_y = hand_landmarks.landmark[0].y

                for lm in hand_landmarks.landmark:
                    temp.extend([
                        lm.x - base_x,
                        lm.y - base_y,
                        lm.z
                    ])

            # ===== SCALE NORMALIZATION =====
            max_value = max(abs(x) for x in temp)
            if max_value != 0:
                temp = [x / max_value for x in temp]

            if hand_label == "Left":
                left_hand = temp
            else:
                right_hand = temp

            # Draw landmarks
            draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # ===== COMBINE BOTH HANDS =====
        data = np.array([left_hand + right_hand])

        # ===== ML PREDICTION =====
        prediction = model.predict(data)[0]

        # ===== CONFIDENCE =====
        confidence = max(model.predict_proba(data)[0])

        # ===== STABILITY FILTER =====
        if confidence > 0.75:
            prediction_buffer.append(prediction)

        if len(prediction_buffer) == 10:
            stable_text = max(set(prediction_buffer), key=prediction_buffer.count)

        # ===== DISPLAY OUTPUT =====
        cv2.putText(
            frame,
            f"{stable_text} ({confidence*100:.1f}%)",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )

    cv2.imshow("Advanced Sign Language Translator", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
