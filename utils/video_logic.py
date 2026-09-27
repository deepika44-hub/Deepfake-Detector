import cv2
import random


def analyze_video(video_file):
    """Lightweight video validation and demo score."""

    try:
        cap = cv2.VideoCapture(video_file)

        if not cap.isOpened():
            return 0.0

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return 0.0

        return random.uniform(0.05, 0.25)

    except Exception:
        return 0.0
