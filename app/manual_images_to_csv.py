import os
import cv2
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_ROOT = os.path.join(BASE_DIR, "..", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "manual_csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_landmarks_from_image(image_path):
    import mediapipe as mp

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    image = cv2.imread(image_path)
    if image is None:
        return None

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    hands.close()

    if not results.multi_hand_landmarks:
        return 0, None

    left_hand = [0] * 63
    right_hand = [0] * 63

    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
        hand_label = results.multi_handedness[idx].classification[0].label
        temp = []
        base_x = hand_landmarks.landmark[0].x
        base_y = hand_landmarks.landmark[0].y
        for lm in hand_landmarks.landmark:
            temp.extend([lm.x - base_x, lm.y - base_y, lm.z])

        max_value = max(abs(x) for x in temp) if temp else 1
        if max_value != 0:
            temp = [x / max_value for x in temp]

        if hand_label == "Left":
            left_hand = temp
        else:
            right_hand = temp

    num_hands = len(results.multi_hand_landmarks)
    return num_hands, left_hand + right_hand


def build_csv_from_images(language):
    source_root = os.path.join(DATA_ROOT, language)
    csv_out = os.path.join(OUTPUT_DIR, f"{language.lower()}_manual.csv")

    rows_all = []
    rows_single = []
    rows_double = []
    failed = []

    if not os.path.isdir(source_root):
        raise FileNotFoundError(f"Language folder not found: {source_root}")

    for gesture_name in sorted(os.listdir(source_root)):
        gesture_folder = os.path.join(source_root, gesture_name)
        if not os.path.isdir(gesture_folder):
            continue

        for image_file in sorted(os.listdir(gesture_folder)):
            if not image_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            image_path = os.path.join(gesture_folder, image_file)
            num_hands, feature_vector = extract_landmarks_from_image(image_path)
            if feature_vector is None:
                failed.append(image_path)
                continue

            # keep a combined CSV (same as before) and also single/double splits
            rows_all.append(feature_vector + [gesture_name])
            if num_hands == 1:
                rows_single.append(feature_vector + [gesture_name])
            elif num_hands >= 2:
                rows_double.append(feature_vector + [gesture_name])

    if not rows_all:
        raise ValueError(f"No valid images found in {source_root}")

    # combined CSV (backwards compatible)
    df_all = pd.DataFrame(rows_all)
    df_all.to_csv(csv_out, index=False, header=False)
    print(f"Saved {len(rows_all)} rows to {csv_out}")

    # single-hand CSV
    csv_single = os.path.join(OUTPUT_DIR, f"{language.lower()}_manual_single.csv")
    if rows_single:
        pd.DataFrame(rows_single).to_csv(csv_single, index=False, header=False)
        print(f"Saved {len(rows_single)} single-hand rows to {csv_single}")
    else:
        print("No single-hand rows found")

    # double-hand CSV
    csv_double = os.path.join(OUTPUT_DIR, f"{language.lower()}_manual_double.csv")
    if rows_double:
        pd.DataFrame(rows_double).to_csv(csv_double, index=False, header=False)
        print(f"Saved {len(rows_double)} double-hand rows to {csv_double}")
    else:
        print("No double-hand rows found")
    if failed:
        print(f"Failed to extract landmarks from {len(failed)} images")
        with open(os.path.join(OUTPUT_DIR, f"{language.lower()}_manual_failed.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(failed))

    return csv_out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert manual ASL/ISL image folders into training CSV data"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        choices=["ASL", "ISL"],
        default=["ASL", "ISL"],
        help="Language folders to convert",
    )
    args = parser.parse_args()

    for language in args.languages:
        build_csv_from_images(language)
