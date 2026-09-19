import argparse
import os
import time
import cv2

BASE_DIR = os.path.dirname(__file__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect sign language images manually into ASL/ISL folders"
    )
    parser.add_argument(
        "--language",
        choices=["ASL", "ISL"],
        required=True,
        help="Language folder to save images into",
    )
    parser.add_argument(
        "--gesture",
        required=True,
        help="Gesture name / label for this collection",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Target number of images to capture",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index to use",
    )
    parser.add_argument(
        "--output-dir",
        default="../data",
        help="Base output directory for saved images",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically save frames at a regular interval instead of pressing 's'",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Seconds between automatic saves when --auto is enabled",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    output_root = os.path.join(BASE_DIR, args.output_dir)
    save_dir = os.path.join(output_root, args.language, args.gesture)
    os.makedirs(save_dir, exist_ok=True)

    existing_images = [
        f
        for f in os.listdir(save_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    start_index = len(existing_images) + 1
    saved_count = 0
    target_count = args.count

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(3, 1280)
    cap.set(4, 720)

    last_save = time.time()

    print(f"Saving manual images to: {save_dir}")
    print("Press 's' to save frame, 'q' to quit.")
    if args.auto:
        print(f"Auto mode enabled: saving every {args.interval}s")

    while cap.isOpened() and saved_count < target_count:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        cv2.putText(
            frame,
            f"Language: {args.language}  Gesture: {args.gesture}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Saved: {saved_count}/{target_count}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            "Press 's' to save, 'q' to quit",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (200, 200, 200),
            2,
        )

        if args.auto and time.time() - last_save >= args.interval:
            args_key = ord("s")
            last_save = time.time()
        else:
            args_key = cv2.waitKey(1) & 0xFF

        if args_key == ord("s"):
            image_name = f"{args.gesture}_{start_index:04d}.jpg"
            image_path = os.path.join(save_dir, image_name)
            cv2.imwrite(image_path, frame)
            saved_count += 1
            start_index += 1
            print(f"Saved {saved_count}/{target_count}: {image_path}")

        if args_key == ord("q"):
            print("Quitting manual collection")
            break

        cv2.imshow("Manual Image Collection", frame)

    cap.release()
    cv2.destroyAllWindows()

    print(f"Finished: collected {saved_count} images in {save_dir}")
