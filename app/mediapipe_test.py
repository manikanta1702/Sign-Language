import cv2
import mediapipe as mp

# ===== MEDIAPIPE SETUP =====
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

draw = mp.solutions.drawing_utils

# ===== CAMERA SETUP =====
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)

# HD Resolution
cap.set(3, 1280)
cap.set(4, 720)

# Camera Warmup
for _ in range(3):
    cap.read()

# ===== MAIN LOOP =====
while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Mirror effect
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    hand_count = 0

    if result.multi_hand_landmarks:

        hand_count = len(result.multi_hand_landmarks)

        for hand_landmarks in result.multi_hand_landmarks:

            draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

    # Display Hand Count
    cv2.putText(
        frame,
        f"Hands Detected: {hand_count}",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Instructions
    cv2.putText(
        frame,
        "Press Q to Exit",
        (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )

    cv2.imshow("MediaPipe Hand Tracking Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()