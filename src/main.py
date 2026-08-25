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
    
    processed_this_run = set()
    
    for job in all_fetched_jobs:
        job_id = job["job_id"]
        if job_id not in seen_ids and job_id not in processed_this_run:
            processed_this_run.add(job_id)
            new_seen_ids[job_id] = now_str
            send_telegram_alert(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, job)
            new_alert_count += 1
            
    if new_seen_ids:
        save_seen_ids(filepath, new_seen_ids)
        
    print(f"Summary: Total fetched={len(all_fetched_jobs)} | New alert sent={new_alert_count}")

if __name__ == "__main__":
    main()
