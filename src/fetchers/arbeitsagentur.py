import requests
from typing import List, Dict, Any

def fetch_jobs(keyword: str, location: str) -> List[Dict[str, Any]]:
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    headers = {
        "X-API-Key": "jobboerse-jobsuche",
        "User-Agent": "StudentJobAgent/1.0"
    }
    
    params = {
        "was": keyword,
        "wo": location,
        "angebotsart": 4, # Praktikum / Werkstudent / Abschlussarbeit
        "veroeffentlichtseit": 1, # last 24 hours
        "size": 50
    }
    
    jobs = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get("stellenangebote", []):
            refnr = item.get("refnr", "")
            job_id = f"aa_{refnr}"
            title = item.get("titel", "")
            company = item.get("arbeitgeber", "")
            arbeitsort = item.get("arbeitsort", {}).get("ort", "Germany")
            
            externe_url = item.get("externeUrl")
            job_url = externe_url if externe_url else f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{refnr}"
            
            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": arbeitsort,
                "url": job_url,
                "source": "Bundesagentur für Arbeit"
            })
    except Exception as e:
        print(f"Error fetching from Arbeitsagentur for '{keyword}': {e}")
        
    return jobs
