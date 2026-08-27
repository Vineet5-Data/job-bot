import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, JOB_LOCATION, KEYWORDS
from storage import load_seen_ids, save_seen_ids
from notifier import send_telegram_alert
# arbeitsagentur kept on disk but no longer imported: its public API key
# returns HTTP 403 everywhere (see note in main()).
from fetchers import jobspy_scraper
import re

# Terms specific enough that two of them in a description mean the role really
# is data/ML work. Deliberately excludes generic words ("data", "analytics",
# "agent", "digital") that appear in almost every German job posting.
STRONG_TECH_KWS = [
    "machine learning", "deep learning", "data science", "data scientist",
    "kuenstliche intelligenz", "künstliche intelligenz", "maschinelles lernen",
    "neuronale netze", "neural network", "computer vision", "natural language",
    "nlp", "reinforcement learning", "large language model", "llm", "genai",
    "generative ai", "pytorch", "tensorflow", "scikit", "sklearn", "keras",
    "pandas", "numpy", "hugging face", "langchain", "xgboost", "lightgbm",
    "jupyter", "matplotlib", "databricks", "mlops", "mlflow",
    "predictive model", "prognosemodell", "datenanalyse", "data analysis",
    "data mining", "statistical model", "statistische", "regression",
    "clustering", "classification", "klassifikation", "zeitreihen",
    "time series", "forecasting", "knowledge graph", "recommender",
    "anomaly detection", "feature engineering", "model training",
    "datenvisualisierung", "power bi", "tableau", "sql", "python",
]

def is_relevant_job(job_dict: dict) -> bool:
    t = job_dict.get("title", "").lower()
    loc = job_dict.get("location", "").lower()
    
    # Block jobs outside Germany (LinkedIn sponsored jobs often bypass location)
    foreign_countries = ["italy", "italia", "france", "uk ", "united kingdom", "spain", "poland", "netherlands", "switzerland", "austria", "usa", "united states", "india"]
    if any(f in loc for f in foreign_countries):
        return False
        
    # Exclude lower priority or irrelevant roles
    if "sales" in t or "marketing" in t or "business development" in t or "e-commerce" in t:
        return False

    # Must be Master Thesis, Internship, or Werkstudent (working student)
    role_kws = [
        "master", "thesis", "abschlussarbeit", "intern", "praktik",
        "werkstudent", "working student", "student",
        # Entry routes that were silently dropped: "Trainee Quality
        # Engineering", "Junior Data Analyst" etc. matched no role keyword.
        "trainee", "graduate", "absolvent", "hilfskraft", "hiwi",
        "duales studium", "dualer", "berufseinsteiger", "young professional",
    ]
    has_role = any(r in t for r in role_kws)
    
    # Must be in Data/AI domain
    tech_kws = [
        # Core (English)
        "data", "machine learning", "deep learning", "nlp", "computer vision",
        "reinforcement", "llm", "robotics", "autonomous", "adas", "genai",
        "generative ai", "artificial intelligence", "agent", "analytics", "audio",
        "speech", "voice", "acoustic",
        "statistic", "quantitative", "econometric", "bayesian", "predictive modeling",
        "predictive maintenance", "time series", "forecasting", "business intelligence",
        "power bi", "tableau", "process mining", "mlops", "model deployment",
        "feature engineering", "tinyml", "neural", "object detection",
        "image recognition", "image segmentation", "pose estimation", "sensor fusion",
        "recommender system", "anomaly detection", "knowledge graph", "embedding",
        "chatbot", "prompt engineering", "fine-tuning", "finetuning",
        "retrieval augmented generation", "foundation model", "sagemaker", "digital twin",
        # German market terms
        "statistik", "datenanalyse", "datenvisualisierung", "zeitreihenanalyse",
        "prädiktiv", "vorhersage", "prognosemodell", "textanalyse", "bilderkennung",
        "bildverarbeitung", "mustererkennung", "objekterkennung", "sprachverarbeitung",
        "künstliche intelligenz", "maschinelles lernen", "neuronale netze",
        "digitaler zwilling", "vorausschauende wartung", "vektordatenbank",
    ]
    # Title-only matching threw away real student roles whose tech stack is
    # stated only in the body ("Werkstudent im Bereich Research & Development").
    # Role still must match the TITLE -- descriptions carry "Praktikum"
    # boilerplate constantly and would match nearly everything.
    # Two-tier matching. A tech term in the TITLE is a deliberate signal, so
    # the full list applies there. A DESCRIPTION is different: nearly every
    # German posting says "Daten" or "Analytics" somewhere, and applying the
    # full list to body text passed 60% of everything -- including
    # "Werkstudent Cyber and IT Security" and "Embedded Systems". Descriptions
    # therefore require TWO distinct STRONG terms.
    has_tech = any(tk in t for tk in tech_kws) or bool(
        re.search(r'\b(ai|ml|cv|ki|rl|etl|rag)\b', t)
    )
    if not has_tech:
        desc = job_dict.get("description", "").lower()
        has_tech = len({k for k in STRONG_TECH_KWS if k in desc}) >= 2
    
    return has_role and has_tech


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment variables.")
        return

    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seen_jobs.json")
    seen_ids = load_seen_ids(filepath)
    new_seen_ids = {}
    
    all_fetched_jobs = []
    
    for keyword in KEYWORDS:
        print(f"Fetching jobs for keyword: {keyword}...")
        # Arbeitsagentur disabled 2026-08-27: the public "jobboerse-jobsuche"
        # API key now returns HTTP 403 on every endpoint, header set, source IP
        # and TLS fingerprint tested, including its OAuth token endpoint. It
        # contributed 0 of 1628 jobs while costing one failed request per
        # keyword per run. Google Jobs (via jobspy) replaces the German-board
        # coverage it was supposed to provide.
        js_jobs = jobspy_scraper.fetch_jobs(keyword, JOB_LOCATION)
        all_fetched_jobs.extend(js_jobs)
        
    new_alert_count = 0
    now_str = datetime.utcnow().isoformat() + "Z"
    

    processed_this_run = set()
    
    for job in all_fetched_jobs:
        job_id = job["job_id"]
        if job_id not in seen_ids and job_id not in processed_this_run:
            processed_this_run.add(job_id)
            new_seen_ids[job_id] = now_str
            
            # Apply strict title filtering
            if is_relevant_job(job):
                send_telegram_alert(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, job)
                new_alert_count += 1
            else:
                print(f"Skipped irrelevant job: {job['title']}")
            
    if new_seen_ids:
        save_seen_ids(filepath, new_seen_ids)
        
    print(f"Summary: Total fetched={len(all_fetched_jobs)} | New alert sent={new_alert_count}")

if __name__ == "__main__":
    main()
