import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, JOB_LOCATION, KEYWORDS
from storage import load_seen_ids, save_seen_ids
from notifier import send_telegram_alert
from fetchers import arbeitsagentur, jobspy_scraper

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
        aa_jobs = arbeitsagentur.fetch_jobs(keyword, JOB_LOCATION)
        js_jobs = jobspy_scraper.fetch_jobs(keyword, JOB_LOCATION)
        all_fetched_jobs.extend(aa_jobs)
        all_fetched_jobs.extend(js_jobs)
        
    new_alert_count = 0
    now_str = datetime.utcnow().isoformat() + "Z"
    
    import re
    def is_relevant_job(job_dict: dict) -> bool:
        t = job_dict.get("title", "").lower()
        loc = job_dict.get("location", "").lower()
        
        # Block jobs outside Germany (LinkedIn sponsored jobs often bypass location)
        foreign_countries = ["italy", "italia", "france", "uk ", "united kingdom", "spain", "poland", "netherlands", "switzerland", "austria", "usa", "united states", "india"]
        if any(f in loc for f in foreign_countries):
            return False
            
        # Exclude lower priority or irrelevant roles
        if "werkstudent" in t or "working student" in t:
            return False
        if "sales" in t or "marketing" in t or "business development" in t or "e-commerce" in t:
            return False
            
        # Must be Master Thesis or Internship
        role_kws = ["master", "thesis", "abschlussarbeit", "intern", "praktik"]
        has_role = any(r in t for r in role_kws)
        
        # Must be in Data/AI domain
        tech_kws = ["data", "machine learning", "deep learning", "nlp", "computer vision", "reinforcement", "llm", "robotics", "autonomous driving", "agentic", "generative ai"]
        has_tech = any(tk in t for tk in tech_kws) or bool(re.search(r'\b(ai|ml|cv|ki|rl|adas|genai)\b', t))
        
        return has_role and has_tech

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
