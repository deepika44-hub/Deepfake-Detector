from transformers import pipeline
from PIL import Image

print("Loading AI Model...")

image_detector = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection"
)


def analyze_image(image_file):
    """Takes an uploaded image and returns a deepfake probability score."""

    img = Image.open(image_file)

    results = image_detector(img)

    fake_score = 0.0

    for result in results:
        if result["label"].lower() == "fake":
            fake_score = result["score"]

    return fake_score
