import cv2
import mediapipe as mp
import csv
import os
import threading
import time

# ========= CONFIG =========
GESTURE_NAME = "A"      # CHANGE THIS EACH TIME
SAMPLES = 300           # Increase samples for better accuracy
DATA_DIR = "../data/raw2"
# ==========================

os.makedirs(DATA_DIR, exist_ok=True)
csv_path = os.path.join(DATA_DIR, f"{GESTURE_NAME}.csv")

# MediaPipe setup (deferred)
mp_hands = mp.solutions.hands
hands = None


def init_mediapipe():
    global hands
    try:
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    except Exception as e:
        print("MediaPipe init error:", e)

# Camera setup (optimized)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
cap.set(cv2.CAP_PROP_CONTRAST, 50)
cap.set(3, 1280)
cap.set(4, 720)

# Start mediapipe init in background and warm-up camera
mp_thread = threading.Thread(target=init_mediapipe, daemon=True)
mp_thread.start()

for _ in range(3):
    cap.read()

count = 0

with open(csv_path, mode="w", newline="") as f:
    writer = csv.writer(f)

    while cap.isOpened() and count < SAMPLES:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # If MediaPipe not initialized yet, show loading overlay
        if hands is None:
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

                    # Normalize position (relative to wrist)
                    base_x = hand_landmarks.landmark[0].x
                    base_y = hand_landmarks.landmark[0].y

                    for lm in hand_landmarks.landmark:
                        temp.extend([
                            lm.x - base_x,
                            lm.y - base_y,
                            lm.z
                        ])

                # Normalize scale
                max_value = max(abs(x) for x in temp)
                if max_value != 0:
                    temp = [x / max_value for x in temp]

                if hand_label == "Left":
                    left_hand = temp
                else:
                    right_hand = temp

            # Combine both hands
            row = left_hand + right_hand
            row.append(GESTURE_NAME)

            writer.writerow(row)
            count += 1

            # Show progress
            cv2.putText(
                frame,
                f"Collecting {GESTURE_NAME}: {count}/{SAMPLES}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2
            )

            # Delay to avoid duplicate frames
            cv2.waitKey(120)

        cv2.imshow("Data Collection (Improved)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
