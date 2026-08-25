import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JOB_LOCATION = os.getenv("JOB_LOCATION", "Deutschland")

KEYWORDS = [
    "Masterarbeit Data Science",
    "Master Thesis Data Science",
    "Masterarbeit Machine Learning",
    "Praktikum Data Science",
    "Internship Data Science",
    "Praktikum Machine Learning"
]
