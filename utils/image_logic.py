from PIL import Image
import random


def analyze_image(image_file):
    """
    Lightweight image analysis for the free Render instance.
    Returns a demo threat score.
    """

    try:
        image = Image.open(image_file)
        image.verify()

        # Lightweight heuristic/demo score.
        # The real ML model can be added later on a larger instance.
        score = random.uniform(0.05, 0.25)

        return score

    except Exception:
        return 0.0
        
