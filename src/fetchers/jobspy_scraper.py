import hashlib
import pandas as pd
from typing import List, Dict, Any

try:
    from jobspy import scrape_jobs
except ImportError:
    scrape_jobs = None

def fetch_jobs(keyword: str, location: str) -> List[Dict[str, Any]]:
    jobs = []
    if not scrape_jobs:
        print("python-jobspy is not installed.")
        return jobs

    try:
        df = scrape_jobs(
            site_name=["linkedin", "indeed", "google"],
            search_term=keyword,
            google_search_term=f"{keyword} jobs in {location}",
            location=location,
            results_wanted=15,
            hours_old=1,
            country_indeed="germany"
        )
        
        if df is None or df.empty:
            return jobs
            
        for _, row in df.iterrows():
            job_url = str(row.get("job_url", ""))
            job_id_val = row.get("id")
            if not pd.isna(job_id_val) and job_id_val:
                job_id = f"li_{job_id_val}"
            else:
                job_id = f"li_{hashlib.sha1(job_url.encode()).hexdigest()}"
                
            from datetime import datetime, timedelta
            date_posted = row.get("date_posted")
            is_old = False
            if pd.notna(date_posted):
                try:
                    dp = pd.to_datetime(date_posted).tz_localize(None)
                    if datetime.utcnow() - dp > timedelta(hours=24):
                        is_old = True
                except Exception:
                    pass
            if is_old:
                continue

            jobs.append({
                "job_id": job_id,
                "title": str(row.get("title", "")),
                "company": str(row.get("company", "")),
                "location": str(row.get("location", "")),
                "url": job_url,
                # Relevance is decided on title + description: German student
                # postings are routinely titled "Werkstudent im Bereich R&D"
                # with every tech term living in the body text.
                "description": str(row.get("description", "") or "")[:4000],
                "source": str(row.get("site", "") or "LinkedIn / Indeed"),
            })
    except Exception as e:
        print(f"Error fetching from JobSpy for '{keyword}': {e}")
        
    return jobs
