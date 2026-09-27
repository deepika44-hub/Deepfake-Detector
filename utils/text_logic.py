import time
import random


def analyze_text(text):
    """Scans text for phishing attempts and psychological manipulation tactics."""

    time.sleep(1.5)

    text = text.lower()

    suspicious_keywords = [
        "urgent",
        "password",
        "otp",
        "bank",
        "account suspended",
        "click here",
        "winner",
        "prize",
        "free",
        "claim",
        "login",
        "police",
        "arrest",
        "bitcoin",
        "crypto",
        "investment"
    ]

    threat_level = sum(
        1 for word in suspicious_keywords
        if word in text
    )

    if threat_level >= 2:
        return random.uniform(0.85, 0.99)

    elif threat_level == 1:
        return random.uniform(0.50, 0.84)

    else:
        return random.uniform(0.01, 0.20)
