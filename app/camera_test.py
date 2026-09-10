import cv2

# Open camera immediately
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FPS, 30)
#cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)
#cap.set(cv2.CAP_PROP_CONTRAST, 50)

# High-quality capture
cap.set(3, 1280)
cap.set(4, 720)

# Warm-up
for _ in range(3):
    cap.read()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Resize for faster processing (optional)

    cv2.imshow("Camera Test (HD)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
