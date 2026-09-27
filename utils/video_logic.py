import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

print("Loading video deepfake model...")

video_detector = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection"
)


def analyze_video(video_file):
    """
    Extracts frames from a video and analyzes them for deepfake probability.
    Returns the average fake score.
    """

    # Save uploaded file temporarily
    video_path = "temp_video.mp4"

    with open(video_path, "wb") as f:
        f.write(video_file.read())

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Unable to open video file")

    fake_scores = []
    frame_count = 0

    while True:
        success, frame = cap.read()

        if not success:
            break

        # Analyze every 10th frame
        if frame_count % 10 == 0:

            # OpenCV BGR → RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame_rgb)

            results = video_detector(image)

            for result in results:
                if result["label"].lower() == "fake":
                    fake_scores.append(result["score"])

        frame_count += 1

        # Limit analysis to 30 frames
        if len(fake_scores) >= 30:
            break

    cap.release()

    if not fake_scores:
        return 0.0

    average_fake_score = float(np.mean(fake_scores))

    return average_fake_score
