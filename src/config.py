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
    "Praktikum Machine Learning",
    "Masterarbeit Deep Learning",
    "Master Thesis Deep Learning",
    "Internship Deep Learning",
    "Masterarbeit Reinforcement Learning",
    "Masterarbeit NLP",
    "Internship NLP",
    "Master Thesis Computer Vision",
    "Internship Machine Learning",
    "Praktikum Data Engineering",
    "Internship Data Analyst",
    "Masterarbeit AI",
    
    # German variants to help with Arbeitsagentur
    "Masterarbeit Künstliche Intelligenz",
    "Masterarbeit KI",
    "Praktikum Künstliche Intelligenz",
    "Praktikum KI",
    "Abschlussarbeit Data Science",
    "Abschlussarbeit Machine Learning",
    "Abschlussarbeit KI",
    
    # Advanced Tech / Autonomous Driving / GenAI (from history)
    "Masterarbeit Autonomous Driving",
    "Internship Autonomous Driving",
    "Master Thesis Generative AI",
    "Masterarbeit GenAI",
    "Masterarbeit RL",
    "Internship Data Analytics",
    "Master Thesis Agentic",
    "Masterarbeit ADAS"
]
